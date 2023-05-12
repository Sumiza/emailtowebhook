from spf import check2
from requests import post
from os import environ
from json import dumps, loads
from email.message import MIMEPart
from email.parser import Parser
from email.policy import default
from aiosmtpd.smtp import SMTP as SMTPServer
from aiosmtpd.smtp import Envelope as SMTPEnvelope
from aiosmtpd.smtp import Session as SMTPSession
from aiosmtpd.controller import Controller
from dkim import verify
from time import sleep, time
from hashlib import sha256
from hmac import digest

loggerlevel = environ.get('LOGGER','INFO').upper()
if loggerlevel == 'INFO':
    loggerlevel = 20
elif loggerlevel == 'DEBUG':
    loggerlevel = 10
elif loggerlevel == 'OFF':
    loggerlevel = 9999
else:
    raise ValueError(f'LOGGER can only be INFO, DEBUG or OFF was {loggerlevel}')

host = environ.get('HOST','0.0.0.0')
port = int(environ.get('PORT',25))

def genlist(envstring:str) -> list:
    if envstring:
        envstring = envstring.replace(" ","").split(',')
    return envstring

target_email = genlist(environ.get('TARGET_EMAIL',None))
source_email = genlist(environ.get('SOURCE_EMAIL',None))

spf_allow_list = genlist(environ.get('SPF_ALLOW_LIST',None))

dkim_reject = bool(environ.get('DKIM_REJECT',False))

ident = environ.get('IDENT','')
email_size = int(environ.get('EMAIL_SIZE',5048576))

webhook = environ.get('WEBHOOK_URL',None)
webhook_headers = environ.get('WEBHOOK_HEADERS',{})
if webhook_headers:
    webhook_headers = loads(webhook_headers)

hmac_secret = environ.get('HMAC_SECRET',None)

def sendmessage(message,level):
    if level >= loggerlevel:
        print(message,flush=True)

class Logger: # TODO add write to file, keep format the same as logging
    def info(message): sendmessage(message,20)
    def debug(message): sendmessage(message,10)

class InboundChecker:
    async def handle_RCPT(self, server, session: SMTPSession, envelope: SMTPEnvelope, address :str, rcpt_options):
        
        def endslist(testends:str, testlist:list) -> bool:
            for i in testlist:
                if testends.endswith(i):
                    return True
            return False

        if target_email:
            if not endslist(address,target_email):
                Logger.debug(f'556 Not accepting for that domain: {address} : {envelope.mail_from}')
                return '556 Not accepting for that domain'
        
        if source_email:
            if not endslist(envelope.mail_from,source_email):
                Logger.debug(f'550 Not accepting emails from your email: {envelope.mail_from} : {address}')
                return '550 Not accepting emails from your email'                
        
        self.spf_answer = check2(i=session.peer[0],
                        s=envelope.mail_from,
                        h=session.host_name,verbose=False)
        
        if spf_allow_list:
            Logger.debug(f'SPF record is {self.spf_answer} : {envelope.mail_from} : {address}')
            if self.spf_answer[0] not in spf_allow_list:
                return f'550 Refused because SPF record is {self.spf_answer}'
            
        envelope.rcpt_tos.append(address)

        Logger.info(f'Accepted connection from {session.peer[0]}, for {address}, from {envelope.mail_from}')        
        return '250 OK' 

    async def handle_DATA(self, server: SMTPServer, session: SMTPSession, envelope: SMTPEnvelope):
        
        global webhook_headers # Dirty fix but is needed in case there is no addon
        global webhook

        email:MIMEPart = Parser(policy=default).parsestr(envelope.content.decode('utf8', errors='replace'))

        dkimverify = verify(envelope.content)
        
        if dkim_reject:
            Logger.debug(f'DKIM is: {dkimverify} : {envelope.mail_from} : {envelope.rcpt_tos[0]}')
            if dkimverify is False:
                return '550 DKIM failed email is rejected'

        def payload(part):
            body = email.get_body(preferencelist=(part))
            if body:
                return body.get_payload(decode=False)
            return None
        
        email_dict = {}
        for i in email.keys():
            email_dict[i] = email.get(i)
        email_dict['Spf'] = self.spf_answer
        email_dict['Dkim-Pass'] = dkimverify
        email_dict['Session-IP'] = session.peer[0]
        email_dict['From-RCPT'] = envelope.mail_from
        email_dict['To-RCPT'] = envelope.rcpt_tos[0]
        email_dict['Bodyplain'] = payload('plain')
        email_dict['Bodyhtml'] = payload('html')
        email_dict['Raw'] = envelope.content.decode('utf8', errors='replace')

        try:
            from addon import Addon
        except: Logger.debug("No Addon found") # no addon found
        else:
            parsed = Addon(email,session,envelope,email_dict,webhook,webhook_headers)
            
            email_dict = parsed.email_dict
            webhook_headers = parsed.webhook_headers
            webhook = parsed.webhook

            if parsed.addon_send_response is not None:
                return parsed.addon_send_response

        if webhook:
            if hmac_secret:
                hmactime = str(time())
                hmac_digest = digest(f'{hmac_secret+hmactime}'.encode(),dumps(email_dict).encode(),sha256).hex()
                webhook_headers['HMAC-Time'] = hmactime
                webhook_headers['HMAC-Signature'] = hmac_digest
            
            Logger.debug(dumps(email_dict,indent=4))
            res = post(webhook,json=email_dict,headers=webhook_headers,timeout=90)
            Logger.info(res.text)

        else:
            Logger.info(dumps(email_dict,indent=4))

        return '250 Message accepted'

if __name__ == '__main__':
    import ssl
    host_name = environ.get('HOST_NAME',None)
    starttls_req = bool(environ.get('TLS_REQUIRED',False))
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain('cert.pem', 'key.pem')
    except:
        context = None
        Logger.debug("TLS not loaded")

    controller = Controller(InboundChecker(),
                            server_hostname=host_name,
                            hostname=host,
                            port=port,
                            ident=ident,
                            data_size_limit=email_size,
                            tls_context=context,
                            require_starttls=starttls_req)
    controller.start()
    while True:
        sleep(100)
