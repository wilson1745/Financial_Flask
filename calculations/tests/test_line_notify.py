import requests

from calculations.common.utils.constants import NOTIFY_LINK, TOKEN_FUNDS, TOKEN_NOTIFY

headers = {
    "Authorization": "Bearer " + TOKEN_FUNDS,
    "Content-Type": "application/x-www-form-urlencoded"
}
params = {
    "message": "\nHAHAHAHAHA"
}

response = requests.post(NOTIFY_LINK, headers=headers, params=params, timeout=60)

"""
200 => success
414 => message too long
"""
response.close()
