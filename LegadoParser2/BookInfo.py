import json
import sys
from LegadoParser2.RuleUrl.Url import parseUrl, getContent, urljoin
from LegadoParser2.RuleJs.JS import EvalJs
from lxml.etree import HTML
from LegadoParser2.RuleEval import getElements, getString, getStrings
from LegadoParser2.FormatUtils import Fmt

if sys.platform == 'win32':
    from LegadoParser2.html5_parser import parse
else:
    from html5_parser import parse


def getBookInfo(compiledBookSource, url, variables):
    # trimBookSource(compiledBookSource)
    evalJs = EvalJs(compiledBookSource)
    evalJs.loadVariables(variables)
    if compiledBookSource.get('header', None):
        headers = compiledBookSource['header']
    else:
        headers = ''
    urlObj = parseUrl(url, evalJs, headers=headers)
    evalJs.set('baseUrl', url)
    content, __ = getContent(urlObj)
    return parseBookInfo(compiledBookSource, urlObj, content.strip(), evalJs)


def parseBookInfo(bS, urlObj, content, evalJs):
    ruleBookInfo = bS['ruleBookInfo']
    # if not ruleBookInfo:
    #     return {}

    _content = content
    if ruleBookInfo.get('init', None):
        content = getElements(content, ruleBookInfo['init'], evalJs)
        if content:
            content = content[0]
    else:
        if content and content.startswith('<') and content.endswith('>'):
            try:
                content = parse(content, sanitize_names=False)
            except Exception:
                content = HTML(content)
        elif content and content.startswith('{') and content.endswith('}'):
            content = json.loads(content)

    bookInfo = {}
    evalJs.set('baseUrl', urlObj['url'])

    if ruleBookInfo.get('name', None):
        bookInfo['name'] = Fmt.bookName(
            getString(content, ruleBookInfo['name'], evalJs, rawContent=_content))
    if ruleBookInfo.get('author', None):
        bookInfo['author'] = Fmt.author(
            getString(content, ruleBookInfo['author'], evalJs, rawContent=_content))
    if ruleBookInfo.get('kind', None):
        bookInfo['kind'] = ','.join(getStrings(
            content, ruleBookInfo['kind'], evalJs, rawContent=_content)).strip()
    if ruleBookInfo.get('wordCount', None):
        bookInfo['wordCount'] = Fmt.wordCount(
            getString(content, ruleBookInfo['wordCount'], evalJs, rawContent=_content))
    if ruleBookInfo.get('lastChapter', None):
        bookInfo['lastChapter'] = getString(
            content, ruleBookInfo['lastChapter'], evalJs, rawContent=_content)
    if ruleBookInfo.get('intro', None):
        bookInfo['intro'] = Fmt.html(
            getString(content, ruleBookInfo['intro'], evalJs, rawContent=_content))
    if ruleBookInfo.get('coverUrl', None):
        bookInfo['coverUrl'] = urljoin(urlObj['url'], getString(
            content, ruleBookInfo['coverUrl'], evalJs, rawContent=_content))
    if ruleBookInfo.get('tocUrl', None):
        result = getStrings(
            content, ruleBookInfo['tocUrl'], evalJs, rawContent=_content)
        if result:
            bookInfo['tocUrl'] = urljoin(urlObj['finalurl'], result[0])
        else:
            bookInfo['tocUrl'] = urlObj['rawUrl']
    else:
        bookInfo['tocUrl'] = urlObj['rawUrl']
        # bookInfo['tocHtml'] = _content

    bookInfo['bookUrl'] = urlObj['finalurl']
    bookInfo['variables'] = evalJs.dumpVariables()

    return bookInfo
