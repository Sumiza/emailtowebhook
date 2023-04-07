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

host = environ.get('HOST','0.0.0.0')
port = environ.get('PORT',25)

target_email = environ.get('TARGET_EMAIL',None)
source_email = environ.get('SOURCE_EMAIL',None)

spf_allow_list = environ.get('SPF_ALLOW_LIST',[])
if spf_allow_list:
    spf_allow_list = loads(spf_allow_list)

ident = environ.get('IDENT','')
email_size = environ.get('EMAIL_SIZE',5048576)
log_off = environ.get('LOG_OFF',None)

webhook = environ.get('WEBHOOK_URL',None)


class InboundChecker:
    async def handle_RCPT(self, server, session: SMTPSession, envelope: SMTPEnvelope, address :str, rcpt_options):

        if target_email:
            if not address.endswith(target_email):
                return '550 Not accepting for that domain'
        
        if source_email:
            if not envelope.mail_from.endswith(source_email):
                return '550 Not accepting emails from your email'
        
        self.sfp = check2(i=session.peer[0],
                        s=envelope.mail_from,
                        h=session.host_name,verbose=False)
        
        if spf_allow_list:
            if self.sfp[0] not in spf_allow_list:
                return f'550 Refused because SPF record is {self.sfp}'
            
        envelope.rcpt_tos.append(address)

        if log_off is None:
            print(f'Accepted connection from {session.peer[0]}, for {address}, from {envelope.mail_from}',flush=True)
        
        return '250 OK' 

    async def handle_DATA(self, server: SMTPServer, session: SMTPSession, envelope: SMTPEnvelope):

        email:MIMEPart = Parser(policy=default).parsestr(envelope.content.decode('utf8', errors='replace'))

        dkimverify = verify(envelope.content)

        def payload(type):
            body = email.get_body(preferencelist=(type))
            if body:
                return body.get_payload(decode=False)
            return None
        
        jdict = {}
        for i in email.keys():
            jdict[i] = email.get(i)
        jdict['Spf'] = self.sfp
        jdict['dkim_pass'] = dkimverify
        jdict['Session_ip'] = session.peer[0]
        jdict['From_RCPT'] = envelope.mail_from
        jdict['To_RCPT'] = envelope.rcpt_tos[0]
        jdict['bodyplain'] = payload('plain')
        jdict['bodyhtml'] = payload('html')
        jdict['Raw'] = envelope.content.decode('utf8', errors='replace')

        if webhook:
            res = post(webhook,json=jdict)
            if log_off is None:
                print(res,flush=True)
        else:
            print(dumps(jdict,indent=4),flush=True)

        return '250 Message accepted'


controller = Controller(InboundChecker(),hostname=host,port=port,ident=ident,data_size_limit=email_size)
controller.start()
input('Server is running')
controller.stop()
