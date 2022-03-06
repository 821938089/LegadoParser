import json
from json.decoder import JSONDecodeError
import hjson
import ast

# 候选Json解析库
# https://pypi.org/project/json5/


class GSONParseError(Exception):
    '''GSON解析失败'''


def parse(text):
    """
    多种类似Json格式解析
    解析单引号、无引号的类Json字符串
    """
    if isinstance(text, (dict, list)):
        return text
    result = None
    try:
        result = json.loads(text)
        return result
    except JSONDecodeError:
        pass

    if not result:
        try:
            result = ast.literal_eval(text)
            return result
        except Exception:
            pass
    else:
        return result

    if not result:
        try:
            result = hjson.loads(text)
            return dict(result)
        except Exception:
            pass
    else:
        return result

    js = {}
    text = text[1:-1]
    # key-value list
    kvs = text.split(',')
    kvs = [i.strip() for i in kvs]
    for kv in kvs:
        key, value = kv.split(':')
        js[key.strip()] = value.strip()

    if js:
        return js
    else:
        raise GSONParseError('GSON解析失败')


# print(parse('{bid:$.book_id}'))
