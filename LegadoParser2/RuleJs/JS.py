
import json
import traceback
import json
import os
import re
from typing import Dict

from LegadoParser2.config import DEBUG_MODE
from LegadoParser2.RuleJs.jsExtension import getZipStringContent, getStringJs

import sys
if sys.platform == 'win32':
    import LegadoParser2.quickjs as quickjs
    from LegadoParser2.quickjs import Object
else:
    import quickjs
    from quickjs import Object

_jsCache = ''


class EvalJs(object):
    def __init__(self, bS) -> None:
        global _jsCache

        self.bS = bS
        self.context = quickjs.Context()
        self.variables: Dict[str, str] = {}  # 存放put get方法的内容
        if not _jsCache:
            filePath = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(filePath, 'jsExtension.js'), 'r') as f:
                _jsCache = f.read()
                self.context.eval(_jsCache)
        else:
            self.context.eval(_jsCache)

        # 注册 java 函数到 Python 中
        self.context.add_callable('pyPut', self.putVariable)
        self.context.add_callable('pyGet', self.getVariable)
        self.context.add_callable('pyAjax', self.ajax)
        self.context.add_callable('pyGetZipStringContent', getZipStringContent)
        self.context.add_callable('pyGetString', self.getString)

    def set(self, name, value):
        if isinstance(value, (list, dict)):
            # obj = self.context.parse_json(json.dumps(value))
            obj = json.dumps(value)
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
        result = self.context.eval(f'{{{expression}}}')
        if isinstance(result, Object):
            return json.loads(result.json())
        # elif result is None:
        #     return None
        else:
            return str(result)

    def putVariable(self, key, value):
        self.variables[key] = value
        return value

    def getVariable(self, key):
        return self.variables.get(key, '')

    def dumpVariables(self):
        return self.variables.copy()

    def loadVariables(self, variable):
        self.variables = variable.copy()

    def ajax(self, url):
        from LegadoParser2.RuleUrl.Url import parseUrl, getContent
        try:
            if DEBUG_MODE:
                print(url)
            urlObj = parseUrl(url, self)
            content = getContent(urlObj)[0]
        except Exception:
            if DEBUG_MODE:
                print('ajax出错了')
                print(f'ajax url {url}')
                print(traceback.format_exc())
        return content

    def getString(self, rule, isUrl):
        return getStringJs(self.get('result'), self, rule, isUrl)
