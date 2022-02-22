# 将词法分析的规则进行分组

from LegadoParser2.RuleType import RuleType, getRuleType2, getRuleType
from LegadoParser2.Tokenize2 import tokenizer, tokenizerInner
from LegadoParser2.RuleDefault.RuleDefaultEfficient2 import parseIndex, getElementsXpath, getStringsXpath
from lxml.etree import _Element, tostring, XPath, XPathSyntaxError
from cssselect import SelectorSyntaxError, ExpressionError
from LegadoParser2.RuleJsonPath.RuleJsonPath import getJsonPath
from jsonpath_ng.exceptions import JSONPathError
import re
from LegadoParser2 import GSON
from LegadoParser2.config import DEBUG_MODE


def packet(rules):
    """
    对规则进行分组
    """
    groupRules = []
    length = len(rules)
    cursor = 0

    while cursor < length:

        ruleType = getRuleType2(rules, cursor)

        groupRule, cursor = getGroupRule(rules, cursor, ruleType)
        groupRules.append(groupRule)

        cursor += 1
    return groupRules


def getGroupRule(rules, cursor, ruleType):
    groupRule = {
        'type': ruleType,
        'rules': []
    }
    length = len(rules)
    while cursor < length:
        rT = getRuleType2(rules, cursor)
        if rT == ruleType or rT == RuleType.JoinSymbol:
            groupRule['rules'].append(rules[cursor])
        else:
            cursor -= 1
            break
        cursor += 1
    return groupRule, cursor


# 预处理规则
def preProcessRule(packedRules):
    """
    对packet函数返回的规则进行预处理

    参数：
      packedRules - packet函数返回的list



    """
    # 1、处理 && %% || 连接符号
    for ruleObj in packedRules:
        ruleObj['joinSymbol'] = ''
        ruleObj['crossJoin'] = False  # 跨规则组拼接
        subRules = []
        subRule = []
        for i in ruleObj['rules']:
            if i in {'&&', '||', '%%'}:
                if ruleObj['joinSymbol'] == '':
                    ruleObj['joinSymbol'] = i
                subRules.append(subRule)
                subRule = []
                continue
            subRule.append(i)
        subRules.append(subRule)
        if len(subRules[-1]) == 0:
            del subRules[-1]
            ruleObj['crossJoin'] = True
        subRules = list(filter(None, subRules))
        ruleObj['subRules'] = subRules

    # 2、对规则进行预处理，主要是编译xpath jsonpath regex
    captureGroupRegex = re.compile(r'(?<!\\)\$\d')
    for rule in packedRules:
        rule['preProcess'] = {}
        if rule['type'] == RuleType.DefaultOrEnd:
            rule['preProcess'] = {'subRules': []}
            for subRule in rule['subRules']:
                rule['preProcess']['subRules'].append(compileRule(subRule))
        elif rule['type'] == RuleType.Xpath:
            rule['preProcess'] = {'subRules': []}
            for subRule in rule['subRules']:
                rule['preProcess']['subRules'].append(compileRule(subRule))
        elif rule['type'] == RuleType.Json:
            rule['preProcess'] = {'subRules': []}
            for subRule in rule['subRules']:
                rule['preProcess']['subRules'].append(compileRule(subRule))
        elif rule['type'] == RuleType.Regex:
            rule['preProcess'] = {'regexType': '',
                                  'body': {'regex': '', 'reObj': None, 'replacement': '', 'replaceFirst': False}}
            regexRule = rule['subRules'][0]
            length = len(regexRule)

            # ## regex 形式
            if length > 1:
                rule['preProcess']['body']['regex'] = regexRule[1]

            # ## regex ## replacement 形式
            if length > 3:
                rule['preProcess']['body']['replacement'] = regexRule[3]

            # 先假定为replace模式
            rule['preProcess']['regexType'] = 'replace'

            if length == 5 and regexRule[-1] == '###':
                rule['preProcess']['regexType'] = 'onlyOne'

            elif length == 2 and regexRule[0] == ':':
                rule['preProcess']['regexType'] = 'allInOne'

            elif length == 5 and regexRule[-1] == '##':
                rule['preProcess']['body']['replaceFirst'] = True

            elif length == 3 and regexRule[-1] == '####':
                rule['preProcess']['body']['replaceFirst'] = True

            if rule['preProcess']['body']['regex']:
                try:
                    rule['preProcess']['body']['reObj'] = re.compile(
                        rule['preProcess']['body']['regex'])
                except re.error:
                    if DEBUG_MODE:
                        print('preProcessRule 正则表达式编译失败')
                    pass

            if rule['preProcess']['body']['replacement'] and rule['preProcess']['regexType'] == 'replace':
                rule['preProcess']['body']['replacement'] = captureGroupRegex.sub(
                    lambda x: '\\' + x[0][1], rule['preProcess']['body']['replacement'])

        elif rule['type'] == RuleType.Js:
            rule['preProcess'] = {'hasInnerRule': False,
                                  'js': [], 'innerRules': [], 'compiledRules': []}
            for js in rule['rules']:
                if js in {'@js:', '<js>', '</js>'}:
                    continue
                tokenResult = tokenizerInner(js)
                if len(tokenResult) > 1:
                    rule['preProcess']['hasInnerRule'] = True
                rule['preProcess']['js'].append(tokenResult)
                length = len(tokenResult)
                cursor = 0
                innerRule = []
                while cursor < length:
                    ruleType = getRuleType(tokenResult, cursor)
                    if ruleType == RuleType.Inner:
                        innerRule.append((tokenResult[cursor], cursor))
                    cursor += 1
                rule['preProcess']['innerRules'].append(innerRule)

            for i in rule['preProcess']['innerRules']:
                compiledRule = []
                for y in i:
                    compiledRuleObj = getRuleObj([y[0]])
                    r = compiledRuleObj[0]
                    if r['type'] == RuleType.DefaultOrEnd and r['rules'][0] not in {'@', '@@'}:
                        r['type'] = RuleType.Js  # Inner默认规则为Js
                        r['preProcess']['js'] = [r['rules']]
                        r['preProcess']['innerRules'] = []
                        r['preProcess']['compiledRules'] = []
                    compiledRule.append(compiledRuleObj)
                rule['preProcess']['compiledRules'].append(compiledRule)
        elif rule['type'] == RuleType.Format:
            rule['preProcess'] = {'subRules': []}
            for subRule in rule['subRules']:
                formatObj = {
                    'innerRules': [], 'getRules': [], 'regexRules': [], 'jsonRules': [], 'compiledInnerRules': [], 'compiledJsonRules': []}
                length = len(subRule)
                cursor = 0
                while cursor < length:
                    ruleType = getRuleType(rule['subRules'][0], cursor)
                    if ruleType == RuleType.Inner:
                        formatObj['innerRules'].append(
                            (rule['subRules'][0][cursor], cursor))
                    elif ruleType == RuleType.Get:
                        formatObj['getRules'].append(
                            (rule['subRules'][0][cursor], cursor))
                    elif ruleType == RuleType.Regex:
                        # allInOne 的 $1
                        formatObj['regexRules'].append(
                            (rule['subRules'][0][cursor], cursor))
                    elif ruleType == RuleType.JsonInner:
                        formatObj['jsonRules'].append(
                            (rule['subRules'][0][cursor], cursor))
                    cursor += 1
                for i in formatObj['innerRules']:
                    formatObj['compiledInnerRules'].append(getRuleObj(i[0]))
                for i in formatObj['jsonRules']:
                    formatObj['compiledJsonRules'].append(getRuleObj(i[0]))
                rule['preProcess']['subRules'].append(formatObj)
        elif rule['type'] == RuleType.Put:
            rule['preProcess'] = {'putRules': {}, 'compiledPutRules': {}}
            length = len(rule['subRules'][0])
            if length == 3:
                rule['preProcess']['putRules'] = GSON.parse('{' + rule['subRules'][0][1] + '}')
                for key, value in rule['preProcess']['putRules'].items():
                    rule['preProcess']['compiledPutRules'][key] = getRuleObj(value)
        elif rule['type'] == RuleType.Order:
            rule['preProcess'] = {'reverse': False}
            if rule['rules'][0] == '-':
                rule['preProcess']['reverse'] = True

    return packedRules


def compileRule(rules):

    length = len(rules)
    cursor = 0
    compiledRules = []

    while cursor < length:
        ruleType = getRuleType(rules, cursor)
        ruleObj = {
            'rule': rules[cursor],
            'type': ruleType,
            'parsedIndex': None,
            'xpath': None,
            'endXpath': None,
            'jsonPath': None,
            'regex': None,
            'replacement': None

        }

        if ruleType == RuleType.DefaultOrEnd:
            indexList, endPos = parseIndex(rules[cursor])

            ruleObj['parsedIndex'] = (indexList, endPos)
            ruleObj['rule'] = rules[cursor][:endPos]
            try:
                path = getElementsXpath(rules[cursor][:endPos])
                if path:
                    ruleObj['xpath'] = XPath(path)
            except XPathSyntaxError:
                pass
            except SelectorSyntaxError as e:
                if DEBUG_MODE:
                    print(f'css 错误{e}')
                pass
            except ExpressionError as e:
                if DEBUG_MODE:
                    print(f'不支持的选择器：{e}')
                    raise
                pass
            except IndexError:
                pass
            try:
                if cursor + 1 == length or rules[cursor + 1] in {'&&', '%%', '||'}:
                    endPath = getStringsXpath(rules[cursor])
                    if endPath:
                        ruleObj['endXpath'] = XPath(endPath)

            except XPathSyntaxError:
                pass
            except SelectorSyntaxError:
                pass
            except ExpressionError as e:
                if DEBUG_MODE:
                    print(f'不支持的选择器：{e}')
                    raise
                pass
            except IndexError:
                pass
            try:
                if length == 1:
                    ruleObj['jsonPath'] = getJsonPath(rules[cursor])
            except JSONPathError:
                pass

        elif ruleType == RuleType.Xpath:
            try:
                path = rules[cursor]
                if path[0] != '.':
                    path = '.' + path
                ruleObj['xpath'] = XPath(path)
            except XPathSyntaxError as e:
                pass
                # print(f'compileRule 发生异常 {e}')

        elif ruleType == RuleType.Json:
            try:
                ruleObj['jsonPath'] = getJsonPath(rules[cursor])
            except JSONPathError as e:
                if DEBUG_MODE:
                    print(f'compileRule 解析jsonpath失败 {e}')
                pass

        cursor += 1
        compiledRules.append(ruleObj)
    return compiledRules


def getRuleObj(rule):
    return preProcessRule(packet(tokenizer(rule)))


def trimBookSource(bS):
    for k in bS:
        if isinstance(bS[k], str):
            bS[k] = bS[k].strip()
        elif isinstance(bS[k], dict):
            trimBookSource(bS[k])


# print(packet(tokenizer('[property=\"og:description\"]@content##(^|[。！？]+[”」）】]?)##$1<br>')))
# print(packet(tokenizer('@js:\nvar doc = org.jsoup.Jsoup.parse(result)\nvar url = \"https://www.imiaobige.com\"+doc.select(\"a\").get(0).attr(\"href\")\nvar all = org.jsoup.Jsoup.parse(java.ajax(url))\nresult = all.select(\"#bookimg\").select(\"img\").attr(\"src\")')))
# print(packet(tokenizer('#readerlists li a<js></js>123{{}}132{{}}')))
# print(
#     packet(tokenizer('https://api.97yd.com/reader?&bookid=@get:{bid}&chapterid={{$.chapterid}}@put:{}')))
# print(packet(
#     tokenizer("{{$.latest_chapter_title}}·{{java.timeFormat(java.getString('$.update_time')*1000)}}")))
# print(packet(
#     tokenizer("{{$.latest_chapter_title}}·{{java.timeFormat(java.getString('$.update_time')*1000)}}")))
# print(packet(tokenizer(
#     "##[\\s\\S]*##<br>★★★ 超星·出版 ★★★<br>★★★ 本书暂无简介 ★★★####[\\s\\S]*##<br>★★★ 超星·出版 ★★★<br>★★★ 本书暂无简介 ★★★###")))
# print(packet(tokenizer(
#     "text####[\\(（【].*?[求更谢乐发订合补加].*?[】）\\)]|正文.")))
# print(packet(tokenizer(
#     "$.book_name@put:{bid:book_id}")))
# print(packet(tokenizer(
#     ":\\{\"C\":(\\d+),.+?,\"N\":\"(.*?)\"[^T]*T\":(\\d{13})[^V]*V\":(\\d)[^\\}]*")))
# pprint.pprint(getRuleObj("#yuedu td.0@li%%td.1@li%%td.2@li"), width=10)
# pprint.pprint(getRuleObj(
#     "/modules/article/search.php,{\n  \"charset\": \"gbk\",\n  \"method\": \"POST\",\n  \"body\": \"searchtype=articlename&searchkey={{key}}&action=login&submit={{key}}&page={{page}}\"\n}"), width=10)
# pprint.pprint(getRuleObj("$4!$2@js:result.replace(/0!/, '').replace(/1!/, '💰')"))
# pprint.pprint(getRuleObj("https://vipreader.qidian.com/chapter/@get:{id}/$1"))
# pprint.pprint(getRuleObj("👁️{{@.count@text}}"))

# print(json.dumps(getRuleObj("👁️{{@.count@text}}"), indent=4, cls=RuleObjectEncoder))
