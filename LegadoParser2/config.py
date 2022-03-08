# 常量存放

from webdriver_manager.utils import get_browser_version_from_os, ChromeType
from webdriver_manager.logger import _init_logger
import logging

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

DEBUG_MODE = True

_init_logger(logging.NOTSET)
CAN_USE_WEBVIEW = get_browser_version_from_os(ChromeType.GOOGLE) != 'UNKNOWN'

if not CAN_USE_WEBVIEW:
    print('未找到Google Chrome浏览器，已禁用webView。')

if DEBUG_MODE:
    print('!!! 警告:你正处于调试模式下运行')
