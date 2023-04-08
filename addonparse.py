class Parse():
    def __init__(self,email,dkimverify,session,envelope,email_dict) -> None:
        self.email = email
        self.dkimverify = dkimverify
        self.session = session
        self.envelope = envelope
        self.email_dict = email_dict
