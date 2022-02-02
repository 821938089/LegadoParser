
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Comment
from lxml.html import html5parser
from lxml.html.html5parser import HTMLParser
from lxml.etree import tostring, _Element, HTML
from html5_parser import parse


def getElementsByDefault(content, compileRule):
    if isinstance(content, str):
        try:
            content = parse(content, treebuilder='soup')
        except:
            content = BeautifulSoup(content, 'html5lib')
    elif isinstance(content, list):
        _content = []
        for c in content:
            _content += getElementsByDefault(c, compileRule)
        return _content

    indexList, endPos = compileRule['parsedIndex']
    compileRule = compileRule['rule'][:endPos]

    if compileRule == '':
        content = content.contents
    # elif not content.contents:
    #     return [content]
    else:
        subRules = compileRule.split('.')
        if subRules[0] == 'children':
            content = content.contents
        elif subRules[0] == 'class':
            if content.has_attr('class') and ' '.join(content['class']) == subRules[1]:
                content = [content] + content.find_all(class_=subRules[1])
            else:
                content = content.find_all(class_=subRules[1])
            content = [i for i in content if ' '.join(i['class']) == subRules[1]]
        elif subRules[0] == 'id':
            if content.has_attr('id') and ' '.join(content['id']) == subRules[1]:
                content = [content] + content.find_all(id=subRules[1])
            else:
                content = content.find_all(id=subRules[1])
        elif subRules[0] == 'tag':
            if content.name == subRules[1]:
                content = [content] + content.find_all(subRules[1])
            else:
                content = content.find_all(subRules[1])
        elif subRules[0] == 'text':
            content = [i.parent for i in content.find_all(text=subRules[1])]
        else:
            content = content.select(compileRule)

    if content and len(indexList):
        try:
            content = selectByIndex(indexList, content)
        except IndexError as e:
            print(f'selectByIndex索引出错 {e}')
            return []

    return content
    pass


def getStringsByDefault(content, rule):
    if isinstance(content, _Element):
        content = BeautifulSoup(tostring(content), 'lxml')
    elif isinstance(content, list):
        _content = []
        for c in content:
            _content += getStringsByDefault(c, rule)
        return _content
    if rule == 'text':
        return [content.text]
    elif rule == 'textNodes':
        return ['\n'.join(i.text.strip() for i in content.descendants if isinstance(i, NavigableString) and not isinstance(i, Comment))]
    elif rule == 'ownText':
        return [''.join(i.text for i in content.contents if isinstance(i, NavigableString) and not isinstance(i, Comment))]
    elif rule == 'html':
        for i in content.select('script'):
            i.decompose()
        for i in content.select('style'):
            i.decompose()
        return [str(content)]
    elif rule == 'all':
        return [str(content)]
    else:
        value = []
        if content.has_attr(rule):
            value.append(content[rule])
        for i in content.find_all(lambda x: x.has_attr(rule)):
            v = i[rule]
            if v not in value:
                value.append(v)
        return value


def selectByIndex(indexList, content):
    length = len(content)
    _content = [None for i in range(len(content))]
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
    return list(filter(None, content))
