# -*- coding: UTF-8 -*-
import time
import traceback

import requests
from requests import ConnectTimeout

from calculations import LOG
from calculations.common.utils.constants import IMAGE_PATH, NOTIFY_LINK, YYYYMMDD_SLASH
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_notifytok import NotifyTok
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor


class LineUtils:
    """ Line notify http utils """

    @interceptor
    def __init__(self, *args):
        """ Constructor """
        # NotifyTok.MINE => 防呆
        self.token = args[0] if len(args) > 0 else NotifyTok.MINE
        # self.token = NotifyTok.MINE

    @interceptor
    def send_mine(self, msg: str):
        """ Sending message to me """
        ms_date = DateUtils.default_msg(YYYYMMDD_SLASH)
        self.send_msg([ms_date, msg], NotifyTok.MINE)

    @interceptor
    def send_msg(self, msg: list, tok: NotifyTok = None):
        """ Sending message through Line client """
        LOG.debug(f"send_msg: {msg}")

        try:
            # Decide Line token
            token = self.token if tok is None else tok

            headers = {
                "Authorization": "Bearer " + token.getValue(),
                "Content-Type": "application/x-www-form-urlencoded"
            }
            params = {
                "message": ("\n".join(msg))
            }

            response = requests.post(NOTIFY_LINK, headers=headers, params=params, timeout=180)

            """
            200 => success
            414 => message too long
            """
            LOG.debug(f"Response status: {response.status_code}")
            response.close()
        except (ConnectTimeout, ConnectionResetError, requests.exceptions.ConnectionError) as error:
            LOG.warning(f"send_msg msg: {msg}")
            CoreException.show_error(error, traceback.format_exc())
            time.sleep(10)
            # (FIXME 觀察一陣子)使用[遞歸]重新進行，直到成功為止 (https://www.cnblogs.com/Neeo/articles/11520952.html#urlliberror)
            self.send_msg(msg)
        except Exception:
            raise
        finally:
            time.sleep(2)

    @interceptor
    def send_img(self, img: str):
        """ Sending picture through Line client """
        try:
            headers = {
                'Authorization': 'Bearer ' + self.token.getValue(),
            }
            data = ({
                'message': [f"{DateUtils.default_msg(YYYYMMDD_SLASH)} {img}! 👍"]
            })
            file = {
                'imageFile': open((IMAGE_PATH % f"{img}.png"), 'rb')
            }

            response = requests.post(NOTIFY_LINK, headers=headers, files=file, data=data, timeout=180)

            """
            200 => success
            414 => message too long
            """
            LOG.debug(f"Response status: {response.status_code}")
            response.close()
        except (ConnectTimeout, ConnectionResetError, requests.exceptions.ConnectionError) as error:
            LOG.warning(f"send_img: {img}")
            CoreException.show_error(error, traceback.format_exc())
            time.sleep(10)
            self.send_img(img)
        except Exception:
            raise
        finally:
            time.sleep(2)
