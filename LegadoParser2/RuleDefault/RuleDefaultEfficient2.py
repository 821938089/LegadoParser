import re
import sys

from lxml.html import tostring
from lxml.etree import HTML
from lxml.cssselect import CSSSelector
# from LegadoParser2.FormatUtils import Fmt
from LegadoParser2.RuleType import RuleType
from LegadoParser2.config import DEBUG_MODE
if sys.platform == 'win32':
    from LegadoParser2.html5_parser import parse
else:
    from html5_parser import parse

# 高效Html处理
# 高效Html5解析器，但是Windows下安装非常繁琐
# https://html5-parser.readthedocs.io/en/latest/


def getElementsByDefault(content, compileRule):
    if isinstance(content, str):
        try:
            content = parse(content, sanitize_names=False)
        except:
            content = HTML(content)
    elif isinstance(content, list):
        _content = []
        for c in content:
            _content += getElementsByDefault(c, compileRule)
        return _content

    # indexList, endPos = parseIndex(rule)
    indexList, endPos = compileRule['parsedIndex']
    rule = compileRule['rule'][:endPos]
    Xpath = compileRule['xpath']

    if Xpath is None:
        if DEBUG_MODE:
            print(f'getElementsByDefault : Xpath 为 None')
        return []

    if rule == '':
        content = list(content)
    # elif not len(content):
    #     return [content]
    else:
        subRules = rule.split('.')
        if subRules[0] in {'tag', 'class', 'id', 'text'}:
            # print(tostring(content, encoding='utf-8').decode())
            content = Xpath(content)

        elif subRules[0] == 'children':
            # https://lxml.de/api/lxml.etree._Element-class.html#getchildren
            content = list(content)

        else:
            content = Xpath(content)
    if content and len(indexList):
        try:
            content = selectByIndex(indexList, content)
        except IndexError as e:
            if DEBUG_MODE:
                print(f'索引出错 {e}')
            return []
    return content


# def getStringsByDefault(content, compileRule):

#     if isinstance(content, list):
#         _content = []
#         for c in content:
#             _content += getStringsByDefault(c, compileRule)
#         return _content
#     rule = compileRule['rule']
#     Xpath = compileRule['endXpath']
#     textRegex = re.compile('\n\s+')
#     if rule == 'text':

#         # return [getText(content)]
#         return [''.join([textRegex.sub('', i) for i in Xpath(content)])]
#         # return [tostring(content, method='text', encoding='utf-8').decode('utf-8')]
#     elif rule == 'textNodes':

#         return ['\n'.join([i.strip() for i in Xpath(content)])]
#     elif rule == 'ownText':
#         # return [getOwnText(content)]
#         return [''.join(Xpath(content))]
#     elif rule == 'html':
#         for i in Xpath(content):
#             i.getparent().remove(i)
#         return [tostring(content, encoding='utf-8', method='html', with_tail=False).decode('utf-8')]
#     elif rule == 'all':
#         return [tostring(content, encoding='utf-8', method='html', with_tail=False).decode('utf-8')]
#     else:
#         return Xpath(content)


def getStringsByDefault(content, compileRule):
    if isinstance(content, str):
        try:
            content = parse(content, sanitize_names=False)
        except:
            content = HTML(content)
    if not isinstance(content, list):
        content = [content]
    rule = compileRule['rule']
    Xpath = compileRule['endXpath']
    # 按浏览器渲染规范大致处理多数情况下的whitespace
    # 测试书源：书趣小说
    # https://stackoverflow.com/questions/24615355/browser-white-space-rendering
    # https://stackoverflow.com/questions/18502410/how-to-remove-insignificant-whitespace-in-lxml-html
    # https://stackoverflow.com/questions/12863588/when-does-whitespace-matter-in-html
    # https://stackoverflow.com/questions/588356/why-does-the-browser-renders-a-newline-as-space
    # https://www.w3.org/TR/REC-html40/struct/text.html#h-9.1
    # https://www.w3.org/TR/CSS21/text.html#white-space-model

    whiteSpaceRegex = re.compile(r'\s+')
    results = []
    for c in content:
        if rule == 'text':
            # results.append(''.join([whiteSpaceRegex.sub(' ', i) for i in Xpath(c)]))
            text = tostring(c, encoding='utf-8', method='text', with_tail=False).decode()
            results.append(whiteSpaceRegex.sub(' ', text))
        elif rule == 'textNodes':
            results.append('\n'.join([i.strip() for i in Xpath(c)]))
        elif rule == 'ownText':
            results.append(''.join(Xpath(c)))
        elif rule == 'html':
            # 删除 script style 标签
            for i in Xpath(c):
                i.clear(keep_tail=True)
            html = tostring(c, encoding='utf-8', method='html', with_tail=False
                            ).decode('utf-8').replace('<br>', '\n<br>')
            # html = Fmt.scriptStyleRegex.sub('', html)
            results.append(html)
        elif rule == 'all':
            results.append(tostring(c, encoding='utf-8', method='html', with_tail=False
                                    ).decode('utf-8'))
        else:
            rs = Xpath(c)
            for r in rs:
                if r not in results:
                    results.append(r)
    return results


def selectByIndex(indexList, content):
    if len(indexList) == 1:
        operate, start, end, step = indexList[0]
        if operate == '.' and (end, step) == (None, None):
            return [content[start]]

    length = len(content)
    # _content = [None for i in range(len(content))]
    _content = [None] * len(content)
    selected = False

    for item in indexList:
        operate, start, end, step = item
        if (start, end) == (-1, 0) and not step:
            content.reverse()
            _content.reverse()
            continue
        if start and start < 0:
            start += length
        if end and end < 0:
            end += length + 1
        rg = None
        if operate == '.':
            selected = True
        if (end, step) == (None, None):
            try:
                if operate == '!':
                    content[start] = None
                elif operate == '.':
                    _content[start] = content[start]
                    content[start] = None
            except IndexError:
                pass
        elif step == None:
            rg = range(start, end)
        else:
            rg = range(start, end, step)
        if rg:
            for i in rg:
                try:
                    if operate == '!':
                        content[i] = None
                    elif operate == '.':
                        _content[i] = content[i]
                        content[i] = None
                except IndexError:
                    pass

    if selected:
        for i in range(length):
            if content[i] == None:
                _content[i] == None
        content = _content
    return list(filter(lambda x: x != None, content))


# def checkIndex(indexList, maxIndex):
#     for idx, item in enumerate(indexList.copy()):
#         operate, start, end, step = item
#         if (end, step) == (None, None):
#             if start > maxIndex:
#                 del indexList[idx]
#         elif step == None:
#             if end > maxIndex:
#                 del indexList[idx]


def parseIndex(rule):
    # 统一索引结构
    indexs = []
    endPos = 0

    def parseSlice(operate):
        nonlocal endPos, rule, index, indexs
        try:
            if index.find(':') != -1:
                n = ['-1' if not i else i for i in index.split(':')]
                if len(n) == 2:
                    indexs.append((operate, int(n[0]), int(n[1]), None))
                elif len(n) == 3:
                    indexs.append((operate, int(n[0]), int(n[1]), int(n[2])))
            else:
                indexs.append((operate, int(index), None, None))
            # endPos = rule.rfind(operate)
            return True
        except ValueError:
            return False

    def parseIndex(operate):
        nonlocal endPos, rule, index, indexs
        try:
            n = index.split(':')
            for i in n:
                indexs.append((operate, int(i), None, None))

            return True
        except ValueError:
            return False

    if rule.find('.') != -1:
        index = rule.split('.')[-1]
        if parseIndex('.'):
            endPos = rule.rfind('.')
    if rule.find('!') != -1 and rule[-1] != ']':
        i = rule.rfind('!')
        index = rule[i + 1:]
        if parseIndex('!'):
            endPos = rule.rfind('!')
    if endPos == 0 and rule[-1] == ']':
        i = rule.rfind('[')
        endPos = i
        indexList = rule[i + 1:-1].replace(' ', '').split(',')
        for index in indexList:
            if index[0] == '!':
                index = index[1:]
                parseSlice('!')
            else:
                parseSlice('.')
    if endPos == 0:
        endPos = len(rule)
    return indexs, endPos


def getElementsXpath(rule):
    subRules = rule.split('.')
    if subRules[0] == 'tag':
        # return f".//{subRules[1]}"
        return CSSSelector(subRules[1]).path
    elif subRules[0] == 'class':
        # return f'.//*[contains(@class,"{subRules[1]}")]'
        return CSSSelector('.' + subRules[1].strip().replace(' ', '.')).path
    elif subRules[0] == 'id':
        # return f".//*[contains(@id,'{subRules[1]}')]"
        return CSSSelector('#' + subRules[1].strip()).path
    elif subRules[0] == 'text':
        return f'.//text()[contains(., "{subRules[1]}")]/parent::*'
    else:
        return CSSSelector(rule).path


def getStringsXpath(rule):

    if rule == 'textNodes':
        return './text()'
    elif rule == 'ownText':
        return './text()'
    elif rule == 'text':
        return './/text()'
    elif rule == 'html':
        return './/script|.//style'
    else:
        return f'.//@{rule}'
    # print(parseIndex('a.b! 1:10 :2'))
    # print(parseIndex('a.b. 1:10:2'))
    # print(parseIndex('a.b[!1:10:2]'))
    # print(parseIndex('a.b[!1:10:2,!3]'))
    # print(parseIndex('a.b[!1:10 :2 ,!3,!4]'))
    # print(parseIndex('[!1:10 :2 ,!3,!4]'))
    # print(parseIndex('!1'))


def defaultProcessor(content, ruleObj, hasEndRule=False):
    # rules = ruleObj['rules']
    joinSymbol = ruleObj['joinSymbol']
    subRules = ruleObj['preProcess']['subRules']
    crossJoin = ruleObj['crossJoin']
    lastResultList = []  # 上一个规则组的结果
    resultList = []
    if isinstance(content, list) and isinstance(content[-1], tuple):
        lastResultList = content[:-1]
        joinSymbol, content = content[-1]
        if lastResultList and joinSymbol == '||':
            return lastResultList

    _content = content

    # if hasEndRule == False:
    #     getFunction = getElementsByDefault
    # else:
    #     getFunction = getStringsByDefault

    for subRule in subRules:
        for compileRule in subRule:
            ruleType = compileRule['type']
            if ruleType == RuleType.DefaultOrEnd:
                if hasEndRule and compileRule['endXpath']:
                    _content = getStringsByDefault(_content, compileRule)
                else:
                    _content = getElementsByDefault(_content, compileRule)
        resultList.append(_content)
        if joinSymbol == '||' and _content:
            break
        _content = content
    if joinSymbol == '%%':
        # 列表转置 https://blog.csdn.net/qq_31375855/article/details/107335919
        resultList = list(map(list, zip(*resultList)))
    # 列表扁平 https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-a-list-of-lists
    resultList = flatten(resultList)
    lastResultList += resultList
    resultList = lastResultList
    if crossJoin:
        resultList.append((joinSymbol, content))
    return resultList


def flatten(t):
    return [item for sublist in t for item in sublist]


# def getText(elements):
#     textList = []
#     regex = re.compile(r'\n\s*')

#     def recGetText(elements):
#         if elements.tag == 'br':
#             textList.append('\n')
#         if elements.text:
#             textList.append(regex.sub('', elements.text))
#         for e in elements:
#             recGetText(e)
#         if elements.tail:
#             textList.append(regex.sub('', elements.tail))

#     recGetText(elements)
#     if textList:
#         return ''.join(textList[:-1]).strip()
#     else:
#         return ''


# def getOwnText(elements):
#     tlst = []
#     regex = re.compile(r'\n\s*')
#     for e in elements:
#         if e.tag == 'br':
#             tlst.append('\n')
#         if e.text:
#             tlst.append(regex.sub('', elements.text))
#         if e.tail:
#             tlst.append(regex.sub('', elements.tail))
#     return ''.join(tlst).strip()
