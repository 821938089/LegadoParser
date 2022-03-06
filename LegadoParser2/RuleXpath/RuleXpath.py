import sys
# from lxml.html import Element, tostring, html5parser
# from lxml.html.html5parser import HTMLParser
from lxml.etree import HTML
from LegadoParser2.RuleType import RuleType
from LegadoParser2.config import DEBUG_MODE
if sys.platform == 'win32':
    from LegadoParser2.html5_parser import parse
else:
    from html5_parser import parse


def getElementsByXpath(content, rule):

    Xpath = rule['xpath']
    if isinstance(content, str):
        # https://stackoverflow.com/questions/2558056/how-can-i-parse-html-with-html5lib-and-query-the-parsed-html-with-xpath
        # https://bugs.launchpad.net/lxml/+bug/1483006
        # 一个7年前的bug，至今仍未修复
        # content = html5parser.fromstring(content, parser=HTMLParser(namespaceHTMLElements=False))
        try:
            content = parse(content, sanitize_names=False)
        except Exception:
            content = HTML(content)

    elif isinstance(content, list):
        _content = []
        for c in content:
            _content += getElementsByXpath(c, rule)
        return _content

    if Xpath is None:
        if DEBUG_MODE:
            print(f'getElementsByDefault : Xpath 为 None')
        return []

    return Xpath(content)


def xpathProcessor(content, rule):
    joinSymbol = rule['joinSymbol']
    subRules = rule['preProcess']['subRules']
    crossJoin = rule['crossJoin']
    lastResultList = []  # 上一个规则组的结果
    resultList = []
    if content and isinstance(content, list) and isinstance(content[-1], tuple):
        lastResultList = content[:-1]
        joinSymbol, content = content[-1]
        if lastResultList and joinSymbol == '||':
            return lastResultList

    _content = content

    for subRule in subRules:
        for compileRule in subRule:
            ruleType = compileRule['type']
            if ruleType == RuleType.Xpath:
                _content = getElementsByXpath(_content, compileRule)
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
