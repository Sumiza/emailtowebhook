# Inbound Email Checker
The Inbound Email Checker is a Python script that can be used to check incoming emails for various properties, such as SPF and DKIM verification, before accepting them. It can also send the email to a webhook, or print it to the console, depending on the configuration.

## Prerequisites
To use this script, you will need the following:

- Python 3.7 or higher
- The spf package
- The requests package
- The aiosmtpd package
- The dkim package

## Environment Variables
The following environment variables should be set to configure the Inbound Checker:

- `HOST`: The IP address or hostname to bind the SMTP server to. Defaults to `0.0.0.0`.
- `PORT`: The port number to bind the SMTP server to. Defaults to `25`.
- `TARGET_EMAIL`: An optional email address to filter incoming emails by. If set, the SMTP server will only accept emails that are addressed to this email address.
- `SOURCE_EMAIL`: An optional email address to filter incoming emails by. If set, the SMTP server will only accept emails that are sent from this email address.
- `SPF_ALLOW_LIST`: An optional JSON-formatted string containing a list of allowed SPF responses `['pass', 'permerror', 'fail', 'temperror', 'softfail', 'none', 'neutral' ]`.
- `DKIM_REJECT`: An optional boolean value indicating whether to reject emails that fail DKIM verification. If set to anything, any email that fails DKIM verification will be rejected. If not set, emails will not be rejected based on DKIM verification.
- `IDENT`: An optional string that will be used as the identity string for the SMTP server. Defaults to an empty string.
- `EMAIL_SIZE`: An optional integer value indicating the maximum size of an incoming email, in bytes. Defaults to `5048576`.
- `LOG_OFF`: An optional boolean value indicating whether to disable console logging. If set to `True`, console logging will be disabled. If not set, or set to any other value, console logging will be enabled.
- `WEBHOOK_URL`: An optional string containing the URL of a webhook to send incoming emails to. If set, the SMTP server will send incoming emails to this webhook.
- `WEBHOOK_HEADERS`: An optional JSON-formatted string containing a dictionary of headers to include in the webhook request. If set, the headers in this dictionary will be added to the webhook request.
- `HMAC_SECRET`: An optional string containing a secret key to use for HMAC validation of the webhook request. If set, the webhook request will include an HMAC signature for validation.

## Usage
To use the Inbound Checker, simply run the Python script. The SMTP server will bind to the specified host and port and begin accepting incoming emails.

Incoming emails will be checked for SPF and DKIM verification, and filtered according to the configuration specified in the environment variables. If an incoming email passes all checks, it will be sent to the webhook URL specified in the environment variables, or printed to the console, depending on the configuration.
