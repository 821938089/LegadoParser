from LegadoParser2.Tokenize2 import tokenizerUrl
from LegadoParser2.RuleType import RuleType
from copy import deepcopy
from LegadoParser2.RulePacket import preProcessRule, packet
from LegadoParser2.config import DEBUG_MODE
from functools import lru_cache


@lru_cache
def getUrlRuleObj(rule):
    return preProcessRule(packet(tokenizerUrl(rule)))


def getStrings(content, rulesObj, evalJs):
    try:
        for rule in rulesObj:
            if rule['type'] == RuleType.DefaultOrEnd:
                pass
            elif rule['type'] == RuleType.Js:
                content = jsProcessor(content, evalJs, rule)
            elif rule['type'] == RuleType.Format:
                content = formatProcrssor(content, rule, evalJs)

        if isinstance(content, str):
            content = [content]
    except Exception:
        if DEBUG_MODE:
            raise
        else:
            content = ['']

    return content


def getString(content, rulesObj, evalJs):
    return '\n'.join(getStrings(content, rulesObj, evalJs))


def formatProcrssor(content, rule, evalJs):
    # 处理 {{ }}
    resultList = []
    joinSymbol = rule['joinSymbol']
    preProcessSubRules = rule['preProcess']['subRules']
    subRules = rule['subRules']
    for formatObj, subRule in zip(preProcessSubRules, subRules):
        rawRules = subRule.copy()
        innerRules = formatObj['innerRules']

        compiledInnerRules = formatObj['compiledInnerRules']

        for idx, rs in enumerate(compiledInnerRules):
            for r in rs:
                if r['type'] == RuleType.DefaultOrEnd:
                    r['type'] = RuleType.Js  # Inner默认规则为Js
                    r['preProcess']['js'] = [r['rules']]
                    r['preProcess']['innerRules'] = []
                    r['preProcess']['compiledRules'] = []
            rawRules[innerRules[idx][1]] = getString(content, rs, evalJs)
            rawRules[innerRules[idx][1] - 1] = ''
            rawRules[innerRules[idx][1] + 1] = ''
        resultList.append(''.join(rawRules))
        if joinSymbol == '||':
            break

    return resultList


def jsProcessor(content, evalJs, rule):
    # hasInnerRule = rule['preProcess']['hasInnerRule']
    js = deepcopy(rule['preProcess']['js'])

    result = content

    for idx, jlst in enumerate(js):

        evalJs.set('result', result)
        result = evalJs.eval(''.join(jlst))

    if isinstance(result, list):
        return result
    else:
        return [result]
