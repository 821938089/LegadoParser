
from LegadoParser2.RuleType import RuleType
from LegadoParser2.RuleDefault.RuleDefaultEfficient2 import defaultProcessor
from LegadoParser2.RuleXpath.RuleXpath import xpathProcessor
from LegadoParser2.RuleJsonPath.RuleJsonPath import jsonPathProcessor
from LegadoParser2.RuleRegex.RuleRegex import regexProcessor
from LegadoParser2.config import DEBUG_MODE
from lxml.etree import _Element, tostring
from copy import deepcopy


def getElements(content, rulesObj, evalJs):
    if content and content[0] in {'{', ']'} and content[-1] in {'}', ']'}:
        # 当内容是json是默认规则为JsonPath
        for rule in rulesObj:
            if rule['type'] == RuleType.DefaultOrEnd:
                rule['type'] = RuleType.Json
    try:
        reverse = False
        for rule in rulesObj:
            if rule['type'] == RuleType.Put:
                putProcessor(content, rule, evalJs)
        for rule in rulesObj:
            if rule['type'] == RuleType.DefaultOrEnd:
                content = defaultProcessor(content, rule)
            elif rule['type'] == RuleType.Xpath:
                content = xpathProcessor(content, rule)
            elif rule['type'] == RuleType.Json:
                content = jsonPathProcessor(content, rule)
            elif rule['type'] == RuleType.Js:
                content = jsProcessor(content, evalJs, rule)
            elif rule['type'] == RuleType.Regex:
                content = regexProcessor(content, rule)
            elif rule['type'] == RuleType.Order:
                reverse = rule['preProcess']['reverse']
    except:
        if DEBUG_MODE:
            raise
        else:
            content = []
    if reverse:
        content.reverse()
    return content


def getStrings(content, rulesObj, evalJs, **kwargs):
    if isinstance(content, (dict, list)) or (isinstance(content, str) and content and content[0] in {'{', ']'} and content[-1] in {'}', ']'}):
        # 当内容是json是默认规则为JsonPath
        for rule in rulesObj:
            if rule['type'] == RuleType.DefaultOrEnd:
                rule['type'] = RuleType.Json
    try:
        for rule in rulesObj:
            if rule['type'] == RuleType.Put:
                putProcessor(content, rule, evalJs)

        for rule in rulesObj:
            if rule['type'] == RuleType.DefaultOrEnd:
                content = defaultProcessor(content, rule, hasEndRule=True)
            elif rule['type'] == RuleType.Xpath:
                content = xpathProcessor(content, rule)
            elif rule['type'] == RuleType.Json:
                content = jsonPathProcessor(content, rule)
            elif rule['type'] == RuleType.Js:
                content = jsProcessor(content, evalJs, rule, **kwargs)
            elif rule['type'] == RuleType.Format:
                content = formatProcrssor(content, rule, evalJs)
            elif rule['type'] == RuleType.Regex:
                content = regexProcessor(content, rule, **kwargs)
    except:
        if DEBUG_MODE:
            raise
        else:
            content = ['']
            return content
    if content and isinstance(content[-1], tuple):
        content = content[:-1]

    return list(filter(None, content))


def getString(content, rulesObj, evalJs, **kwargs):
    replaceRegexRuleObj = []  # 在regexProcessor中使用
    result = getStrings(content, rulesObj, evalJs,
                        replaceRegexRuleObj=replaceRegexRuleObj, **kwargs)
    result = '\n'.join(result).strip()
    if replaceRegexRuleObj:
        result = regexProcessor(result, replaceRegexRuleObj[0])[0]
    return result


def putProcessor(content, rule, evalJs):
    compiledPutRules = rule['preProcess']['compiledPutRules']
    for key, r in compiledPutRules.items():
        evalJs.putVAR(key, getString(content, r, evalJs))


def jsProcessor(content, evalJs, rule, **kwargs):
    # hasInnerRule = rule['preProcess']['hasInnerRule']
    js = deepcopy(rule['preProcess']['js'])
    innerRules = rule['preProcess']['innerRules']
    compiledRules = rule['preProcess']['compiledRules']

    if isinstance(content, _Element):
        if content.tag == 'html':
            result = kwargs.get('rawContent', '')
        else:
            result = tostring(content, encoding='utf-8').decode('utf-8')
    elif isinstance(content, list):
        try:
            result = ''.join(content)
        except TypeError:
            # content内含一个字典[{...}]
            if content:
                result = content[0]
            pass
    else:
        result = content
    for idx, jlst in enumerate(js):
        if len(compiledRules) and compiledRules[idx]:
            for i, rule in enumerate(compiledRules[idx]):
                jlst[innerRules[idx][i][1]] = getString(content, rule, evalJs)
                jlst[innerRules[idx][i][1] - 1] = ''
                jlst[innerRules[idx][i][1] + 1] = ''

        evalJs.set('result', result)
        result = evalJs.eval(''.join(jlst))
    if isinstance(result, list):
        return result
    else:
        return [result]


def formatProcrssor(content, rule, evalJs):
    # 处理 {{ }}  @get:{ } {$. } $1

    joinSymbol = rule['joinSymbol']
    crossJoin = rule['crossJoin']
    lastResultList = []  # 上一个规则组的结果
    preProcessSubRules = rule['preProcess']['subRules']
    subRules = rule['subRules']
    resultList = []
    if isinstance(content, list) and isinstance(content[-1], tuple):
        lastResultList = content[:-1]
        joinSymbol, content = content[-1]
        if lastResultList and joinSymbol == '||':
            return lastResultList
    for formatObj, subRule in zip(preProcessSubRules, subRules):

        rawRules = subRule.copy()
        innerRules = formatObj['innerRules']
        getRules = formatObj['getRules']
        jsonRules = formatObj['jsonRules']
        regexRules = formatObj['regexRules']
        compiledInnerRules = formatObj['compiledInnerRules']
        compiledJsonRules = formatObj['compiledJsonRules']
        regexRules = formatObj['regexRules']

        for idx, rs in enumerate(compiledInnerRules):
            for r in rs:
                if r['type'] == RuleType.DefaultOrEnd and r['rules'][0] not in {'@', '@@'}:
                    r['type'] = RuleType.Js  # Inner默认规则为Js
                    r['preProcess']['js'] = [r['rules']]
                    r['preProcess']['innerRules'] = []
                    r['preProcess']['compiledRules'] = []
            rawRules[innerRules[idx][1]] = getString(content, rs, evalJs)
            rawRules[innerRules[idx][1] - 1] = ''
            rawRules[innerRules[idx][1] + 1] = ''
        for idx, rs in enumerate(compiledJsonRules):
            for r in rs:
                r['type'] == RuleType.Json
            rawRules[jsonRules[idx][1]] = getString(content, rs, evalJs)
            rawRules[jsonRules[idx][1] - 1] = ''
            rawRules[jsonRules[idx][1] + 1] = ''
        for idx, r in enumerate(regexRules):
            rawRules[regexRules[idx][1]] = content[int(r[0][1]) - 1]
        for idx, r in enumerate(getRules):
            rawRules[getRules[idx][1]] = evalJs.getVAR(r[0])
            rawRules[getRules[idx][1] - 1] = ''
            rawRules[getRules[idx][1] + 1] = ''
        resultList.append(''.join(rawRules))
        if joinSymbol == '||':
            break
    lastResultList += resultList
    resultList = lastResultList
    if crossJoin:
        resultList.append((joinSymbol, content))
    return resultList
