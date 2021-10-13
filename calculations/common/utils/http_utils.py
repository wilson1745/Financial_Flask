# -*- coding: UTF-8 -*-
import socket
import ssl
import time
import traceback
from http.client import HTTPResponse
from urllib.request import urlopen

import requests
from requests import ConnectTimeout

from calculations.common.constants.constants import IMAGE_PATH, NOTIFY_LINK, YYYYMMDD_SLASH
from calculations.common.enums.enum_notifytok import NotifyTok
from calculations.common.exceptions.core_exception import CoreException
from calculations.common.utils.date_utils import DateUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor


class HttpUtils:
    """ Http request and response (include Line notify) """

    @interceptor
    def __init__(self, *args):
        """ Constructor """
        # NotifyTok.MINE => 防呆
        self.token = args[0] if len(args) > 0 else NotifyTok.MINE
        # self.token = NotifyTok.MINE

    @interceptor
    def __push_message(self, link: str, headers=None, params=None, files=None, data=None):
        """ Common for pushing the line messages """
        try:
            if params is not None:
                # Message
                response = requests.post(NOTIFY_LINK, headers=headers, params=params, timeout=180)
            else:
                # Picture
                response = requests.post(NOTIFY_LINK, headers=headers, files=files, data=data, timeout=180)

            """
                200 => success
                414 => message too long
            """
            LOG.debug(f"Response status: {response.status_code}")
            response.close()
        except socket.error as e:
            CoreException.show_warn(e, traceback.format_exc())
            """ 使用[遞歸]重新進行，直到成功為止 (https://www.cnblogs.com/Neeo/articles/11520952.html#urlliberror) """
            time.sleep(10)
            self.__push_message(link, headers=headers, params=params, files=files, data=data)
        except (ConnectTimeout, ConnectionResetError, requests.exceptions.ConnectionError) as e:
            """ Test for observing the process of try and catch """
            LOG.error(f"url_open other error: {e}")
            CoreException.show_warn(e, traceback.format_exc())
            """ 使用[遞歸]重新進行，直到成功為止 (https://www.cnblogs.com/Neeo/articles/11520952.html#urlliberror) """
            time.sleep(10)
            self.__push_message(link, headers=headers, params=params, files=files, data=data)
        except Exception:
            raise
        finally:
            time.sleep(2)

    @classmethod
    @interceptor
    def url_open(cls, url: str, error_sum=0) -> HTTPResponse:
        """ Common for making request and get response (Manage the socket error together) """
        try:
            LOG.debug(f"Url: {url}")
            # 預防urllib.error.URLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
            ssl._create_default_https_context = ssl._create_unverified_context
            response = urlopen(url, timeout=600)
            return response
        # except (socket.error, URLError, HTTPError, requests.exceptions.ConnectionError, ConnectTimeout, ConnectionResetError) as error:
        except socket.error as e:
            # FIXME if the connection error happends too many times, stop the process
            if error_sum > 20:
                raise e
            else:
                error_sum += 1

            CoreException.show_warn(e, traceback.format_exc())
            """ Add 'return' if the function has to return object, or it will return None """
            time.sleep(10)
            return cls.url_open(url, error_sum)
        except Exception:
            raise
        finally:
            time.sleep(7)

    @interceptor
    def send_mine(self, msg: str):
        """ Sending message to me """
        ms_date = DateUtils.default_msg(YYYYMMDD_SLASH)
        self.send_msg([ms_date, msg], NotifyTok.MINE)

    @interceptor
    def send_msg(self, msg: list, tok: NotifyTok = None):
        """ Sending message through Line client """
        LOG.debug(f"send_msg: {msg}")

        """ Decide Line token """
        token = self.token if tok is None else tok

        headers = {
            "Authorization": "Bearer " + token.getValue(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        params = {
            "message": ("\n".join(msg))
        }

        self.__push_message(NOTIFY_LINK, headers=headers, params=params, files=None, data=None)

    @interceptor
    def send_img(self, img: str):
        """ Sending picture through Line client """
        headers = {
            'Authorization': 'Bearer ' + self.token.getValue(),
        }
        data = ({
            'message': [f"{DateUtils.default_msg(YYYYMMDD_SLASH)} {img}! 👍"]
        })
        file = {
            'imageFile': open((IMAGE_PATH % f"{img}.png"), 'rb')
        }

        self.__push_message(NOTIFY_LINK, headers=headers, params=None, files=file, data=data)
