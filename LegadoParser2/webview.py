import os
import subprocess
import sys
import base64
import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
from LegadoParser2.config import DEBUG_MODE
_driver = None


class WebView(object):
    def __init__(self):
        if not self.driver:
            self.driver = getDriverInstance()

    @property
    def driver(self) -> WebDriver:
        global _driver
        return _driver

    @driver.setter
    def driver(self, value):
        global _driver
        _driver = value

    def getResponseByUrl(self, url, javaScript=''):
        self.driver.get(url)
        # 平滑滚动到底
        self.driver.execute_script(
            "window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        time.sleep(0.7)
        if javaScript:
            return self.driver.execute_script(javaScript)
        else:
            return self.driver.page_source

    def getResponseByHtml(self, html, javaScript=''):
        # https://stackoverflow.com/questions/22538457/put-a-string-with-html-javascript-into-selenium-webdriver
        html_bs64 = base64.b64encode(html.encode('utf-8')).decode()
        self.driver.get("data:text/html;base64," + html_bs64)
        self.driver.execute_script(
            "window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        time.sleep(0.7)
        if javaScript:
            return self.driver.execute_script(javaScript)
        else:
            return self.driver.page_source


def getDriverInstance():
    chromePath = getChromePath()
    if sys.platform == 'win32' and chromePath:
        user_data_dir = os.path.join(os.path.abspath("."), 'webview\AutomationProfile')
        if DEBUG_MODE:
            subprocess.Popen(
                f'cmd /c ""{chromePath}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}" --lang=zh-CN --mute-audio --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36""')
        else:
            subprocess.Popen(
                f'cmd /c ""{chromePath}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}" --lang=zh-CN --headless --disable-gpu --mute-audio --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36""')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        options.set_capability("detach", True)
        service = Service(executable_path=ChromeDriverManager(log_level=logging.NOTSET).install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        options = webdriver.ChromeOptions()
        options.set_capability("detach", True)
        if not DEBUG_MODE:
            options.headless = True
        options.add_argument("--mute-audio")
        options.add_argument("--headless")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        service = Service(executable_path=ChromeDriverManager(log_level=logging.NOTSET).install())
        driver = webdriver.Chrome(service=service, options=options)
    return driver


def getChromePath():
    if sys.platform == 'win32':
        chromePath = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chromePath):
            chromePath = r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(chromePath):
            chromePath = ""
    else:
        chromePath = ""
    return chromePath
