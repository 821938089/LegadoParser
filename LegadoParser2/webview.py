import base64
import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from LegadoParser2.config import DEBUG_MODE, USER_AGENT
from urllib.parse import parse_qs
try:
    from LegadoParser2.fontutils import getAllFontFaceUrl
except:
    getAllFontFaceUrl = None

# bot 检测
# https://bot.sannysoft.com/


class WebView(object):
    def __init__(self, userAgent=USER_AGENT):
        self.driver = createDriverInstance(userAgent)
        self.allFontFaceUrl = None

        if DEBUG_MODE:
            global _driver
            try:
                _driver.quit()
            except:
                pass
            _driver = self.driver

    @property
    def currentUrl(self):
        return self.driver.current_url

    def getResponseByUrl(self, url, javaScript=''):
        # 定义 navigator.platform 为空
        # https://stackoverflow.com/questions/38808968/change-navigator-platform-on-chrome-firefox-or-ie-to-test-os-detection-code
        # 在页面加载前执行Js
        # https://stackoverflow.com/questions/31354352/selenium-how-to-inject-execute-a-javascript-in-to-a-page-before-loading-executi
        # https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                                    'source': "Object.defineProperty(navigator,'platform',{value:''})"})
        self.driver.get(url)
        # 平滑滚动到底
        self.driver.execute_script(
            "window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        time.sleep(0.7)
        if javaScript:
            result = ''
            for _ in range(30):
                result = self.driver.execute_script('return ' + javaScript)
                if result:
                    break
                time.sleep(1)
            else:
                if DEBUG_MODE:
                    print('WebView.getResponseByPost js 执行超时')
            return result
        else:
            if getAllFontFaceUrl:
                self.allFontFaceUrl = self.driver.execute_script(getAllFontFaceUrl)
            return self.driver.page_source

    def getResponseByPost(self, url, formData, charset='utf-8', javaScript=''):
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                                    'source': "Object.defineProperty(navigator,'platform',{value:''})"})
        # https://stackoverflow.com/questions/22538457/put-a-string-with-html-javascript-into-selenium-webdriver
        # 注意不能直接设置html，因为baseUrl不正确，相对地址的js资源无法加载
        # 有需要可以手动（用正则）对html里的相对地址改成绝对地址（不建议）
        # 好像可以用iframe手动设置url和html，不知道可不可行
        # https://stackoverflow.com/questions/7534622/select-iframe-using-python-selenium
        html = createPostFormHtml(url, formData, charset)
        html_bs64 = base64.b64encode(html.encode(charset)).decode()
        self.driver.get("data:text/html;base64," + html_bs64)
        self.driver.find_element_by_id('post').click()
        # 跳转后等待加载完成
        # https://stackoverflow.com/questions/36590274/selenium-how-to-wait-until-page-is-completely-loaded
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete")

        if javaScript:
            result = ''
            for _ in range(30):
                result = self.driver.execute_script('return ' + javaScript)
                if result:
                    break
                time.sleep(1)
            else:
                if DEBUG_MODE:
                    print('WebView.getResponseByPost js 执行超时')
            return result
        else:
            return self.driver.page_source


_executable_path = None


def createDriverInstance(userAgent=USER_AGENT):
    options = webdriver.ChromeOptions()
    # user_data_dir = os.path.join(os.path.abspath("."), 'webview\AutomationProfile')
    # options.set_capability("detach", True)
    if not DEBUG_MODE:
        options.headless = True
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--mute-audio")
    # options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--lang=zh-CN,zh")
    # options.add_argument("--disable-application-cache")
    options.add_argument('--ignore-certificate-errors')
    # 禁用 sec-ch-* 协议头
    options.add_argument('--disable-features=UserAgentClientHint')
    # 不显示恢复标签提示
    # https://stackoverflow.com/questions/51269896/selenium-disable-restore-pages-poup
    prefs = {'exit_type': 'Normal'}
    options.add_experimental_option("prefs", {'profile': prefs})
    # 防止打印一些无用的日志
    # https://blog.csdn.net/qq_24269969/article/details/111173932
    options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    # 去除webdriver痕迹
    # https://zhuanlan.zhihu.com/p/328768200
    options.add_argument("disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={userAgent}")
    # https://stackoverflow.com/questions/55376947/how-do-i-ignore-an-alert-using-selenium-chrome-webdriver-python
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    # https://stackoverflow.com/questions/57700388/how-to-set-unexpectedalertbehaviour-in-selenium-python
    options.set_capability('unhandledPromptBehavior', 'accept')
    global _executable_path
    if not _executable_path:
        _executable_path = ChromeDriverManager(log_level=logging.NOTSET)
    service = Service(executable_path=_executable_path.install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def createPostFormHtml(url, formData, charset):
    # https://stackoverflow.com/questions/10494417/making-a-post-request-in-selenium-without-filling-a-form
    source = f'''<html>
    <head>
        <meta charset="{charset}">
    </head>
    <body>
        <form action="{url}" method="post" id="postform">\n'''
    formDict = parse_qs(formData, keep_blank_values=True)
    for name, values in formDict.items():
        for value in values:
            source += f'            <input type="hidden" name="{name}" value="{value}">\n'
    source += '''            <input type="submit" id="post">
        </form>
    </body>
</html>'''
    return source
