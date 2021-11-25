import requests

from calculations.common.constants.constants import NOTIFY_LINK, TOKEN_FUNDS

headers = {
    "Authorization": "Bearer " + TOKEN_FUNDS,
    "Content-Type": "application/x-www-form-urlencoded"
}
params = {
    "message": "\nTest Line Notify (From Wilon's Oracle cloud server!) hehe~~"
}

response = requests.post(NOTIFY_LINK, headers=headers, params=params, timeout=60)

"""
200 => success
414 => message too long
"""
response.close()
