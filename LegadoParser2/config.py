# 常量存放

from webdriver_manager.chrome import ChromeDriverManager
import logging

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

DEBUG_MODE = True

CAN_USE_WEBVIEW = ChromeDriverManager(log_level=logging.NOTSET).driver.browser_version != 'UNKNOWN'

if DEBUG_MODE:
    print('!!! 警告:你正处于调试模式下运行')
