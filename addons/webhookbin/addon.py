
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
        """
            Write your custom parser here
            default sender will use
                self.email_dict
                self.webhook
                self.webhook_headers
        """
        emailfrom = self.email_dict['From']
        emailto = str(self.email_dict['To'])
        bodyplain = self.email_dict['Bodyplain']
        bodyhtml = self.email_dict['Bodyhtml']
        subject = self.email_dict['Subject']
        date = self.email_dict['Date']

        #clean up emailto
        emailto = emailto.split(' ')[-1]
        emailto = emailto.replace('<','').replace('>','')
        emailto = emailto[::-1]
        emailto = emailto.split('@')
        
        #email user
        user = emailto[-1][::-1]

        # figure out bin and password
        emailto = emailto[0].split('.')[2:]
        try: binid = emailto[0][::-1]
        except: binid =  None
        try: binauth = emailto[1][::-1]
        except: binauth = None

        # clear email dict
        self.email_dict = {}

        #build own dict to send as json
        self.email_dict['from'] = emailfrom
        self.email_dict['emailuser'] = user
        self.email_dict['bodyplain'] = bodyplain
        self.email_dict['bodyhtml'] = bodyhtml
        self.email_dict['subject'] = subject
        self.email_dict['date'] = date

        self.webhook_headers = {
                "HideIp": "true",
                "Message_Source":"Email"}
        
        if binauth:
            self.webhook_headers["Binauth"] = binauth
        
        if binid is not None:
            self.webhook = f'https://webhookbin.net/v1/bin/{binid}'
        else:
            self.webhook = None #needs to be cleared for main script

        # self.sender() #to call the custom sender

    def sender(self):
        """
            if this is called then you need to take care of sending by yourself
            this can be to a database, webhook, email.. etc
            self.addon_send_response has to be a smtp response if it stays None
            the default sender will be called after this function.
        """
        self.addon_send_response = '250 Message accepted' # smpt return
