import re
from LegadoParser2.RuleType import getRuleType, RuleType
from itertools import groupby, zip_longest
from lxml.etree import _Element, tostring


# def getElementsByRegex(content, rule):
#     # AllInOne规则
#     return re.findall(rule, content)


# def getStringsByRegex(result, rules, cursor):
#     # OnlyOne 或 Replace 规则

#     # if isinstance(result, list):
#     #     _content = []
#     #     for c in result:
#     #         _c, cursor = getStringsByRegex(c, rules, cursor)
#     #         _content += _c
#     #     return _content, cursor
#     if '###' in rules[0]['rules']:
#         # OnlyOne规则
#         # if isinstance(content, BeautifulSoup):
#         #     content = str(content)
#         # elif isinstance(content, _Element):
#         #     content = tostring(content)
#         # result.clear()
#         pattern = rules[cursor]['rule']
#         replaceStr = rules[cursor + 2]['rule']
#         match = re.search(pattern, '\n'.join(result))
#         result.clear()
#         result.append(re.sub(r'(?<!\\)\$\d', lambda x: match[int(x[0][1])], replaceStr))
#         return cursor + 2
#     else:
#         # Replce规则
#         length = len(rules)
#         regexSet = []
#         while cursor < length:
#             rule = rules[cursor]
#             # ruleType = getRuleType(rules, cursor)
#             ruleType = rule['type']
#             if ruleType == RuleType.RuleSymbol:
#                 pass
#             elif ruleType == RuleType.Regex:
#                 regexSet.append(rule['rule'])
#             else:
#                 # getStrings函数循环完会cursor+1所以需要-1补偿一下，以便规则正常运行
#                 cursor -= 1
#                 break
#             cursor += 1
#         # https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.text/-regex/replace.html
#         captureGroupRegex = re.compile(r'(?<!\\)\$\d')
#         for pattern, replaceStr in grouper(regexSet, 2):
#             for i in range(len(result)):
#                 for m in re.finditer(pattern, result[i]):
#                     old = m[0]
#                     if replaceStr:
#                         new = captureGroupRegex.sub(lambda x: m[int(x[0][1])], replaceStr)
#                     else:
#                         new = ''
#                     result[i] = result[i].replace(old, new)
#         return cursor


def regexProcessor(content, rule, **kwargs):
    regexType = rule['preProcess']['regexType']
    reObj = rule['preProcess']['body']['reObj']
    replacement = rule['preProcess']['body']['replacement']
    regex = rule['preProcess']['body']['regex']
    replaceFirst = rule['preProcess']['body']['replaceFirst']

    if regexType == 'allInOne':
        return reObj.findall(content)
    elif regexType == 'onlyOne':
        if isinstance(content, _Element):
            if content.tag == 'html':
                content = kwargs.get('rawContent', '')
            else:
                content = tostring(content, encoding='utf-8').decode('utf-8')
        elif isinstance(content, list):
            content = '\n'.join(content)
        match = reObj.search(content)
        return [re.sub(r'(?<!\\)\$\d', lambda x:match[int(x[0][1])] if match else "", replacement)]
    elif regexType == 'replace':
        if not isinstance(content, list):
            content = [content]

        content = list(filter(lambda x: isinstance(x, str), content))
        if replaceFirst:
            for i in range(len(content)):
                content[i] = reObj.sub(replacement, content[i], 1)
        else:
            for i in range(len(content)):
                content[i] = reObj.sub(replacement, content[i])
        # if regex == '$':
        #     for i in range(len(content)):
        #         content[i] += replacement
        # else:
        #     captureGroupRegex = re.compile(r'(?<!\\)\$\d')
        #     for i in range(len(content)):
        #         for m in reObj.finditer(content[i]):
        #             old = m[0]
        #             if replacement:
        #                 new = captureGroupRegex.sub(lambda x: m[int(x[0][1])], replacement)
        #             else:
        #                 new = ''
        #             content[i] = content[i].replace(old, new, 1)
        #             if replaceFirst:
        #                 break
        return content


# def grouper(iterable, n, fillvalue=None):
#     # https://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks
#     args = [iter(iterable)] * n
#     return zip_longest(*args, fillvalue=fillvalue)
