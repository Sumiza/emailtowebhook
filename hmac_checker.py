from hmac import digest,compare_digest
from hashlib import sha256
from json import loads,dumps


def hmac_compare(secret:str,signature:str,time:str,content:dict):
    ans = digest(f'{secret+time}'.encode(),
                dumps(content).encode(),
                sha256).hex()
    return compare_digest(ans,signature)

webhook = loads()

is_same = hmac_compare(
    'Secret',
    webhook['headers']['Hmac-Signature'],
    webhook['headers']['Hmac-Time'],
    webhook['content'])