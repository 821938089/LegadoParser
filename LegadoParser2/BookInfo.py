import json
import sys
from LegadoParser2.RuleUrl.Url import parseUrl, getContent, urljoin
from LegadoParser2.RuleJs.JS import EvalJs
from LegadoParser2.RulePacket import getRuleObj, trimBookSource
from lxml.etree import HTML
from LegadoParser2.RuleEval import getElements, getString, getStrings
from LegadoParser2.FormatUtils import Fmt

if sys.platform == 'win32':
    from LegadoParser2.html5_parser import parse
else:
    from html5_parser import parse


def getBookInfo(bS, url):
    trimBookSource(bS)
    evalJs = EvalJs(bS)
    if bS.get('header', None):
        headers = bS['header']
    else:
        headers = ''
    urlObj = parseUrl(url, evalJs, headers=headers)
    evalJs.set('baseUrl', url)
    content, __ = getContent(urlObj)
    return parseBookInfo(bS, urlObj, content.strip(), evalJs)


def parseBookInfo(bS, urlObj, content, evalJs):
    ruleBookInfo = bS['ruleBookInfo']
    if not ruleBookInfo:
        return {}
    if ruleBookInfo.get('name', None):
        rulesName = getRuleObj(ruleBookInfo['name'])
    if ruleBookInfo.get('tocUrl', None):
        rulesTocUrl = getRuleObj(ruleBookInfo['tocUrl'])
    if ruleBookInfo.get('author', None):
        rulesAuthor = getRuleObj(ruleBookInfo['author'])
    if ruleBookInfo.get('kind', None):
        rulesKind = getRuleObj(ruleBookInfo['kind'])
    if ruleBookInfo.get('coverUrl', None):
        rulesCoverUrl = getRuleObj(ruleBookInfo['coverUrl'])
    if ruleBookInfo.get('wordCount', None):
        rulesWordCount = getRuleObj(
            ruleBookInfo['wordCount'])
    if ruleBookInfo.get('intro', None):
        rulesIntro = getRuleObj(ruleBookInfo['intro'])
    if ruleBookInfo.get('lastChapter', None):
        rulesLastChapter = getRuleObj(
            ruleBookInfo['lastChapter'])
    if ruleBookInfo.get('init', None):
        rulesInit = getRuleObj(
            ruleBookInfo['init'])
    _content = content
    if ruleBookInfo.get('init', None):
        content = getElements(content, rulesInit, evalJs)
        if content:
            content = content[0]
    else:
        if content and content.startswith('<') and content.endswith('>'):
            try:
                content = parse(content, sanitize_names=False)
            except:
                content = HTML(content)
        elif content and content.startswith('{') and content.endswith('}'):
            content = json.loads(content)

    bookInfo = {}
    evalJs.set('baseUrl', urlObj['url'])

    if ruleBookInfo.get('name', None):
        bookInfo['name'] = Fmt.bookName(getString(content, rulesName, evalJs, rawContent=_content))
    if ruleBookInfo.get('author', None):
        bookInfo['author'] = Fmt.author(
            getString(content, rulesAuthor, evalJs, rawContent=_content))
    if ruleBookInfo.get('kind', None):
        bookInfo['kind'] = ','.join(getStrings(
            content, rulesKind, evalJs, rawContent=_content)).strip()
    if ruleBookInfo.get('wordCount', None):
        bookInfo['wordCount'] = Fmt.wordCount(
            getString(content, rulesWordCount, evalJs, rawContent=_content))
    if ruleBookInfo.get('lastChapter', None):
        bookInfo['lastChapter'] = getString(content, rulesLastChapter, evalJs, rawContent=_content)
    if ruleBookInfo.get('intro', None):
        bookInfo['intro'] = Fmt.html(getString(content, rulesIntro, evalJs, rawContent=_content))
    if ruleBookInfo.get('coverUrl', None):
        bookInfo['coverUrl'] = urljoin(urlObj['url'], getString(
            content, rulesCoverUrl, evalJs, rawContent=_content))
    if ruleBookInfo.get('tocUrl', None):
        result = getStrings(
            content, rulesTocUrl, evalJs, rawContent=_content)
        if result:
            bookInfo['tocUrl'] = urljoin(urlObj['url'], result[0])
        else:
            bookInfo['tocUrl'] = urlObj['finalurl']
    else:
        bookInfo['tocUrl'] = urlObj['finalurl']
        # bookInfo['tocHtml'] = _content

    return bookInfo
