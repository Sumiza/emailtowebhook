class Parse():
    def __init__(self,email,dkimverify,session,envelope,email_dict,webhook_headers) -> None:
        self.email = email
        self.dkimverify = dkimverify
        self.session = session
        self.envelope = envelope
        self.email_dict = email_dict
        self.webhook_headers = webhook_headers

    ### Write your custom parser here
    # default sender will use self.email_dict and self.webhook_headers







    ###