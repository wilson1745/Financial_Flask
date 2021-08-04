import logging
import logging.handlers
from logging import handlers


class Logger(object):
    # 日誌級別關係映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', when='D', backCount=30,
                 fmt='%(asctime)s - %(levelname)s - %(pathname)s[line:%(lineno)d]: %(message)s'):
        """ Constructor """
        # logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(filename)

        # 設置日誌格式
        format_str = logging.Formatter(fmt)

        # 設置日誌級別
        self.logger.setLevel(self.level_relations.get(level))

        # 往屏幕上輸出
        sh = logging.StreamHandler()

        # 設置屏幕上顯示的格式
        sh.setFormatter(format_str)

        # 往文件裡寫入#指定間隔時間自動生成文件的處理器
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount, encoding='utf-8')
        # 實例化TimedRotatingFileHandler
        # interval是時間間隔
        # backupCount是備份文件的個數，如果超過這個個數，就會自動刪除，
        # when是間隔的時間單位，單位有以下幾種：
        # S 秒
        # M 分
        # H 小時、
        # D 天、
        # W 每星期（interval==0時代表星期一）
        # midnight 每天凌晨

        # 設置文件裡寫入的格式
        th.setFormatter(format_str)

        # 把對象加到logger裡
        self.logger.addHandler(sh)
        self.logger.addHandler(th)

# if __name__ == '__main__':
#     # logg = gen_logger()
#     filePath = ((str(Path(Path(__file__).resolve().parents[1])) + Constants.LOG_PATH) % datetime.now().strftime('%Y_%m_%d'))
#     log = Logger(filePath, level='debug')
#
#     log.logger.debug('debug')
#     log.logger.info('info')
#     log.logger.warning('警告')
#     log.logger.error('報錯')
#     log.logger.critical('嚴重')
#
#     filePathError = (Constants.LOG_PATH % datetime.now().strftime('%Y_%m_%d') + '_error')
#     logEr = Logger(filePathError, level='error')
#
#     logEr.logger.error('error')
