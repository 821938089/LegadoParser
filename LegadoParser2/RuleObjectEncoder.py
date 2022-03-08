import json
import re
from jsonpath_ng import JSONPath
from lxml.etree import XPath
from LegadoParser2.RuleType import RuleType
from LegadoParser2.RuleUrl.BodyType import Body


class RuleObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, re.Pattern):
            return obj.pattern
        elif isinstance(obj, JSONPath):
            return str(obj)
        elif isinstance(obj, XPath):
            return obj.path
        elif isinstance(obj, RuleType):
            return obj.name
        elif isinstance(obj, Body):
            return obj.name
        return json.JSONEncoder.default(self, obj)
