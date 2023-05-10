"""
    Environment Variables Needed:
    TELNYX_KEY = 'KEY4354325243redsgaaegerG_GAefgewafEAWFAGE'
    TELNYX_FROM = '+11231231234'

    Environment Variables Optional:
    SUBJECT_BLACKLIST = 'Invoice, Spam, meeting'  
    TELNYX_TO = '+11231231234'
    DOMAIN_SENDERS =  '{
        "example.com":"+11231231234",
        "sub.example.com":"+19991112222"}'

    REGEX_SUB_REMOVE = '^Hello!\n\n'
    
    If an environment variable is not set for TELNYX_TO
    it will try and pull the number from the first part
    of the to email.
    123-1231234@example.com = +11231231234

"""

from os import environ
from json import loads
from main import genlist,Logger
import re


class Addon():
    def __init__(self,
                email,
                session,
                envelope,
                email_dict,
                webhook,
                webhook_headers) -> None:
        
        self.email = email
        self.session = session
        self.envelope = envelope
        self.email_dict = email_dict
        self.webhook = webhook
        self.webhook_headers = webhook_headers
        self.addon_send_response = None

        self.parse()

    def parse(self):

        # Blackhole if subject had any word from SUBJECT_BLACKLIST
        subject_blacklist = genlist(environ.get('SUBJECT_BLACKLIST',None))
        if subject_blacklist:
            for block in subject_blacklist:
                if self.email_dict['Subject'].casefold().find(block.casefold()) != -1:
                    self.addon_send_response = '250 Message accepted to blackhole'
                    return

        message:str = self.email_dict.get('Bodyplain').strip()

        # Remove the most basic of signatures
        message = message.split('--')[0].strip()

        # Naive removal of the reply part of an email
        def removereply(message:str) -> str:
            output = []
            isreply = False
            for line in message.splitlines():
                if line.startswith('>'):
                    isreply = True
                    break
                output.append(line)
            
            if isreply:
                deleteme = None
                for count,line in enumerate(output):
                    if line.startswith('On'):
                        deleteme = count
                if deleteme:
                    output = output[:deleteme]

            return '\n'.join(output).strip()
        
        # Message to send as text
        message = removereply(message)

        # Run regex 
        subregex = environ.get('REGEX_SUB_REMOVE',None)
        if subregex:
            message = re.sub(fr"{subregex}", "", message, 0, re.MULTILINE)

        # Raise an error if message is longer than 3 sms texts
        length_limit = 160*3
        message_length = len(message)
        if message_length > length_limit:
            raise ValueError(f'Message is too long: {message_length}, limit is {length_limit}')

        # Only for canadian and US numbers
        def phoneformat(phonenumber):
            output = ''
            for i in str(phonenumber):
                if i.isdigit():
                    output += i
            if len(output) == 10:
                return '+1'+output
            if len(output) == 11:
                return '+'+output
            return output

        # Figure out where to send text message to
        tonumber = environ.get('TELNYX_TO',None)

        if tonumber is None: 
            tonumber = self.email_dict['To-RCPT'].split('@')[0]
            tonumber = phoneformat(tonumber)

        # Figure out what to use as from number
        from_domains = environ.get('TELNYX_FROM_DOMAINS',{})
        fromnumber = None
        if from_domains:
            from_domains:dict = loads(from_domains)
            Logger.debug(from_domains)
            Logger.debug(self.email_dict['To-RCPT'].casefold())
            for i in from_domains.keys():
                if self.email_dict['To-RCPT'].casefold().endswith(i.casefold()):
                    fromnumber = from_domains.get(i)
                    break

        # If no match found used the TELNYX_FROM
        if fromnumber is None:
            fromnumber = environ.get('TELNYX_FROM')    

        # clear email dict
        self.email_dict = {}

        # Build dict that will become json to send to telnyx
        self.email_dict['to'] = tonumber
        self.email_dict['from'] = fromnumber
        self.email_dict['text'] = message
        Logger.debug(self.email_dict)
        self.webhook_headers['Authorization'] = 'Bearer '+ environ.get('TELNYX_KEY')
        self.webhook = 'https://api.telnyx.com/v2/messages'
