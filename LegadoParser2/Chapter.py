import json
import sys
from LegadoParser2.FormatUtils import Fmt
from LegadoParser2.RuleUrl.Url import parseUrl, getContent, urljoin
from LegadoParser2.RuleJs.JS import EvalJs
from LegadoParser2.RulePacket import getRuleObj, trimBookSource
from lxml.etree import HTML
from LegadoParser2.RuleEval import getElements, getString, getStrings
from concurrent.futures import ThreadPoolExecutor

if sys.platform == 'win32':
    from LegadoParser2.html5_parser import parse
else:
    from html5_parser import parse


def getChapterContent(bS, url, nextChapterUrl=''):
    trimBookSource(bS)
    evalJs = EvalJs(bS)
    if bS.get('header', None):
        headers = bS['header']
    else:
        headers = ''
    urlObj = parseUrl(url, evalJs, headers=headers)
    content, __ = getContent(urlObj)
    return parseContent(bS, urlObj, content.strip(), evalJs, nextChapterUrl=nextChapterUrl)


def parseContent(bS, urlObj, content, evalJs, **kwargs):
    ruleContent = bS['ruleContent']
    nextChapterUrl = kwargs.get('nextChapterUrl', None)
    if not ruleContent:
        return {}
    if ruleContent.get('content', None):
        rulesContent = getRuleObj(ruleContent['content'])
    if ruleContent.get('nextContentUrl', None):
        rulesNextContentUrl = getRuleObj(ruleContent['nextContentUrl'])
    if ruleContent.get('replaceRegex', None):
        rulesReplaceRegex = getRuleObj(ruleContent['replaceRegex'])

    _content = content

    if content and content.startswith('<') and content.endswith('>'):
        try:
            content = parse(content, sanitize_names=False)
        except:
            content = HTML(content)
    elif content and content.startswith('{') and content.endswith('}'):
        content = json.loads(content)

    chapterContent = {'content': ''}

    def parseCt(content):

        if ruleContent.get('content', None):
            chapterContent['content'] += getString(
                content, rulesContent, evalJs, rawContent=_content)
            chapterContent['content'] += '\n'
        if ruleContent.get('nextContentUrl', None):
            nextContentUrls = getStrings(
                content, rulesNextContentUrl, evalJs, rawContent=_content)
        else:
            nextContentUrls = None

        return nextContentUrls

    nextContentUrls = parseCt(content)

    if nextContentUrls:
        if len(nextContentUrls) == 1:
            nextUrl = urljoin(urlObj['url'], nextContentUrls[0])
            allNextUrls = []
            if nextChapterUrl:
                allNextUrls.append(nextChapterUrl)
            while nextContentUrls and nextUrl not in allNextUrls:
                allNextUrls.append(nextUrl)
                urlObj = parseUrl(nextUrl, evalJs)
                content, __ = getContent(urlObj)
                nextContentUrls = parseCt(content)
                if nextContentUrls:
                    nextUrl = urljoin(urlObj['url'], nextContentUrls[0])
                else:
                    break
        else:
            contents = fetchContents(nextContentUrls)
            for content, __ in contents:
                parseCt(content)

    if chapterContent['content']:
        chapterContent['content'] = Fmt.html(chapterContent['content'])

    if ruleContent.get('replaceRegex', None):
        chapterContent['content'] = getString(
            chapterContent['content'], rulesReplaceRegex, evalJs, rawContent=_content)

    return chapterContent


def fetchContents(urls):
    evalJs = EvalJs({})
    executor = ThreadPoolExecutor(max_workers=8)
    tasks = []
    results = []
    for u in urls:
        urlObj = parseUrl(u, evalJs)
        task = executor.submit(getContent, urlObj)
        tasks.append(task)
    for task in tasks:
        results.append(task.result())
