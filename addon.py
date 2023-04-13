


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
        pass

        # self.sender() to call the custom sender


    def sender(self):
        """
            if this called then you need to care of sending by yourself
            this can be to a database, webhook, email.. etc
            self.addon_send_response has to be a smtp response if it stays None
            the default sender will be called.
        """
        self.addon_send_response = '250 Message accepted' # smpt return


        