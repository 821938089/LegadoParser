from jsonpath_ng import parse
import json
from LegadoParser2.RuleType import RuleType


def getElementsByJsonPath(content, rule):
    if isinstance(content, str):
        content = json.loads(content)
    elif isinstance(content, list):
        _content = []
        for c in content:
            _content += getElementsByJsonPath(c, rule)
        return _content
    jsonPath = rule['jsonPath']
    # if len(rule['preProcess']['subRules'][0]) == 1:
    #     jsonPath = rule['preProcess']['subRules'][0][0]['jsonPath']
    # elif len(rule['preProcess']['subRules'][0]) == 2:
    #     jsonPath = rule['preProcess']['subRules'][0][1]['jsonPath']
    # result = jsonPath.find(content)
    # if result:
    #     value = result[0].value
    #     if isinstance(value, list):
    #         return value
    #     else:
    #         return [str(value)]
    if jsonPath is None:
        return []
    matchs = jsonPath.find(content)
    result = []
    if matchs:
        for match in matchs:
            if isinstance(match.value, list):
                result += match.value
            elif isinstance(match.value, (int, float)):
                result.append(str(match.value))
            else:
                result.append(match.value)
    return result


def getStringsByJsonPath(content, rule):
    # if isinstance(content, str):
    #     content = json.loads(content)
    jsonPath = rule['jsonPath']
    # if len(rule['preProcess']['subRules'][0]) == 1:
    #     jsonPath = rule['preProcess']['subRules'][0][0]['jsonPath']
    # elif len(rule['preProcess']['subRules'][0]) == 2:
    #     jsonPath = rule['preProcess']['subRules'][0][1]['jsonPath']
    # jsonPath = rule['preProcess']['subRules'][0][0]['jsonPath']
    matchs = jsonPath.find(content)
    result = []
    if matchs:
        for match in matchs:
            if isinstance(match.value, list):
                result += match.value
            elif isinstance(match.value, (int, float)):
                result.append(str(match.value))
            else:
                result.append(match.value)
        # value = result[0].value
        # if isinstance(value, list):
        #     return value
        # else:
        #     return [str(value)]
    return result


def jsonPathProcessor(content, rule, getStrings=False):
    joinSymbol = rule['joinSymbol']
    subRules = rule['preProcess']['subRules']
    crossJoin = rule['crossJoin']
    lastResultList = []  # 上一个规则组的结果
    resultList = []
    if isinstance(content, list) and isinstance(content[-1], tuple):
        lastResultList = content[:-1]
        joinSymbol, content = content[-1]
        if lastResultList and joinSymbol == '||':
            return lastResultList

    _content = content

    for subRule in subRules:
        for compileRule in subRule:
            ruleType = compileRule['type']
            if ruleType == RuleType.Json or ruleType == RuleType.DefaultOrEnd:
                if getStrings:
                    _content = getStringsByJsonPath(_content, compileRule)
                else:
                    _content = getElementsByJsonPath(_content, compileRule)
        resultList.append(_content)
        if joinSymbol == '||' and _content:
            break
        _content = content
    if joinSymbol == '%%':
        resultList = list(map(list, zip(*resultList)))

    resultList = flatten(resultList)
    lastResultList += resultList
    resultList = lastResultList
    if crossJoin:
        resultList.append((joinSymbol, content))
    return resultList


def flatten(t):
    return [item for sublist in t for item in sublist]


def getJsonPath(rule):
    return parse(rule)
