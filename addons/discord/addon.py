from os import environ

"""
    Basic email to discord addon
    Takes the ENV DISCORD_IDTOKEN
    example: 
    DISCORD_IDTOKEN = 109691893456346445176/Avuqw05Tmoz9pw8-Efeawf4332c-ooZR3_dy5voHRFgaregGDAgrergL8v5wphMQcMWlVD
    Or just include the whole thing as the webhook ENV
    would include the "?wait=true" at the end to get a response for the log
"""


class Addon():
    def __init__(self,email,session,envelope,email_dict,webhook,webhook_headers) -> None:
        
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
        # there is no real sanitizing done, dont open this to the public
        emailfrom = str(self.email_dict['From']).strip()
        emailbody = str(self.email_dict['Bodyplain']).strip()

        self.email_dict = {"content": emailbody, "username": emailfrom}
        
        discord_idtoken= environ.get('DISCORD_IDTOKEN',None)
        if discord_idtoken:
            self.webhook = "https://discord.com/api/webhooks/"+discord_idtoken+"?wait=true"

        
