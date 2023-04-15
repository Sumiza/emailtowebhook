"""
    Environment Variables Needed:
    TELNYX_KEY = 'KEY4354325243redsgaaegerG_GAefgewafEAWFAGE'
    TELNYX_FROM = '+11231231234'

    Environment Variables Optional:
    TELNYX_TO = '+11231231234'

    If an environment variable is not set for TELNYX_TO
    it will try and pull the number from the first part
    of the to email.
    123-1231234@example.com = +11231231234

"""

from os import environ

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
        message = removereply(message)

        # raise an error if message is longer than 3 sms texts
        length_limit = 160*3
        message_length = len(message)
        if message_length > length_limit:
            raise ValueError(f'Message is too long: {message_length}, limit is {length_limit}')

        # only for canadian and US numbers
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

        tonumber = environ.get('TELNYX_TO',None)

        if tonumber is None: 
            tonumber = self.email_dict['To-RCPT'].split('@')[0]
            tonumber = phoneformat(tonumber)
        
        self.email_dict = {}

        self.email_dict['to'] = tonumber
        self.email_dict['from'] = environ.get('TELNYX_FROM')
        self.email_dict['text'] = message

        self.webhook_headers['Authorization'] = 'Bearer '+ environ.get('TELNYX_KEY')
        self.webhook = 'https://api.telnyx.com/v2/messages'
