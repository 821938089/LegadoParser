import json
from json.decoder import JSONDecodeError
import hjson
import ast


class GSONParseError(Exception):
    '''GSON解析失败'''


def parse(text):
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
        except:
            pass
    else:
        return result

    if not result:
        try:
            result = hjson.loads(text)
            return dict(result)
        except:
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
