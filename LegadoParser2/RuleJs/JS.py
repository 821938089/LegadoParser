
import quickjs
import json
# from LegadoParser2.HttpRequset2 import req
# from httpx._exceptions import RequestError
import traceback
import json
from LegadoParser2.RuleUrl.Url import parseUrl, getContent
from quickjs import Object
import os
from LegadoParser2.config import DEBUG_MODE
from LegadoParser2.RuleJs.jsExtension import getZipStringContent, getStringJs
import re
_jsCache = ''


class EvalJs(object):
    def __init__(self, bS) -> None:
        global _jsCache

        self.bS = bS
        self.context = quickjs.Context()
        self.VAR = {}  # 存放put get方法的内容
        if not _jsCache:
            filePath = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(filePath, 'jsExtension.js'), 'r') as f:
                _jsCache = f.read()
                self.context.eval(_jsCache)
        else:
            self.context.eval(_jsCache)

        self.context.add_callable('pyPut', self.putVAR)
        self.context.add_callable('pyGet', self.getVAR)
        self.context.add_callable('pyAjax', self.ajax)
        self.context.add_callable('pyGetZipStringContent', getZipStringContent)
        self.context.add_callable('pyGetString', self.getString)

    def set(self, name, value):
        if isinstance(value, (list, dict)):
            obj = self.context.parse_json(json.dumps(value))
            self.context.set(name, obj)
        else:
            self.context.set(name, value)
        return self

    def get(self, name):
        result = self.context.get(name)
        if isinstance(result, Object):
            return json.loads(result.json())
        else:
            return result

    def eval(self, expression):
        # print(expression)
        # 替换变量定义中的let和const关键字为var，防止报重复定义变量错误
        varRegex = re.compile(r'(let|const)\s+([a-zA-z_$][\w$]*)(\s*[=;]{0,1})')
        expression = varRegex.sub(r'var \2\3', expression)
        result = self.context.eval(expression)
        if isinstance(result, Object):
            return json.loads(result.json())
        # elif result is None:
        #     return None
        else:
            return str(result)

    def putVAR(self, key, value):
        self.VAR[key] = value
        return value

    def getVAR(self, key):
        try:
            return self.VAR[key]
        except:
            return ''

    def ajax(self, url):
        try:
            if DEBUG_MODE:
                print(url)
            urlObj = parseUrl(url, self)
            content = getContent(urlObj)[0]
        except:
            if DEBUG_MODE:
                print('ajax出错了')
                print(f'ajax url {url}')
                print(traceback.format_exc())
        return content

    def getString(self, rule, isUrl):
        return getStringJs(self.get('result'), self, rule, isUrl)


# def getContent(searchObj):
#     if searchObj['method'] == 'GET':
#         method = 0
#     elif searchObj['method'] == 'POST':
#         method = 1
#     redirected = False
#     try:

#         content, __, respone = req(searchObj['url'], header=searchObj['headers'],
#                                    method=method, post_data=searchObj['body'])
#         searchObj['finalurl'] = str(respone.url)
#         if respone.history:
#             searchObj['redirected'] = True
#         else:
#             searchObj['redirected'] = False

#     except RequestError:
#         raise
#         # exc_type, exc_value, __ = sys.exc_info()
#         # return f'Request Fail: {exc_type} {exc_value}', False
#         return f'Request Fail: {traceback.format_exc()}', False

#     print(respone.status_code)
#     # print(searchObj)
#     # 重定向到了详情页
#     if respone.history:
#         redirected = True
#         return content, redirected
#     else:
#         return content, redirected


# def setDefaultHeaders(headers, bodyType):
#     headerKeys = [k.lower() for k in headers.keys()]
#     if 'user-agent' not in headerKeys:
#         headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     if 'content-type' not in headerKeys:
#         if bodyType == Body.FORM:
#             headers['Content-Type'] = 'application/x-www-form-urlencoded'
#         elif bodyType == Body.JSON:
#             headers['Content-Type'] = 'application/json'


# def parseUrl(bS, url):
#     searchObj = {
#         'url': '',
#         'method': 'GET',
#         'body': '',
#         'headers': {},
#     }
#     baseUrl = bS['bookSourceUrl']
#     bodyType = Body.FORM

#     splitResult = url.split(',', maxsplit=1)

#     if len(splitResult) == 2:
#         url, options = splitResult

#         url = urljoin(baseUrl, url)

#         # 合并dict PEP584：https://www.python.org/dev/peps/pep-0584/
#         searchObj |= GSON.parse(options)
#         if 'header' in bS and bS['header']:
#             searchObj['headers'] |= GSON.parse(bS['header'])

#         if isinstance(searchObj['headers'], str):
#             searchObj['headers'] = json.loads(searchObj['headers'])

#         if isinstance(searchObj['body'], dict):
#             searchObj['body'] = json.dumps(searchObj['body'])
#             bodyType = Body.JSON
#         if searchObj['body'][0] == '{':
#             bodyType = Body.JSON
#         if searchObj['method'].upper() == 'POST':
#             searchObj['bodytype'] = bodyType.name

#     else:

#         url = urljoin(baseUrl, url)

#     setDefaultHeaders(searchObj['headers'], bodyType)
#     if 'charset' not in searchObj:
#         searchObj['charset'] = 'utf-8'

#     searchObj['url'] = url

#     return searchObj


# def urljoin(base, url):
#     # HttpCon = getLeftStr(base, '://')
#     # AddRoot = getMiddleStr(base, '://', '/')
#     if url.startswith('http'):
#         return url
#     HttpCon, AddRoot = base.split('://')
#     AddRoot = AddRoot.split('/')[0]
#     if url[:2] == '//':
#         return HttpCon + url
#     elif url[:1] == '/':
#         return HttpCon + '://' + AddRoot + url
#     else:
#         pos = base.rfind('/')
#         return base[:pos + 1] + url


# class Body(Enum):
#     # 请求体类型
#     JSON = 1
#     FORM = 2
