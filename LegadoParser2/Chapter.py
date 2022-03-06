import json
import sys
from LegadoParser2.FormatUtils import Fmt
from LegadoParser2.RuleUrl.Url import parseUrl, getContent, urljoin
from LegadoParser2.RuleJs.JS import EvalJs
from lxml.etree import HTML
from LegadoParser2.RuleEval import getElements, getString, getStrings
from concurrent.futures import ThreadPoolExecutor
from LegadoParser2.config import DEBUG_MODE
try:
    from LegadoParser2.fontutils import checkPUA, fixPUAStr, collectPUAChars
except ImportError:
    pass
if sys.platform == 'win32':
    from LegadoParser2.html5_parser import parse
else:
    from html5_parser import parse


def getChapterContent(compiledBookSource, url, variables, nextChapterUrl=''):
    # trimBookSource(compiledBookSource)
    ruleContent = compiledBookSource['ruleContent']
    evalJs = EvalJs(compiledBookSource)
    evalJs.loadVariables(variables)
    if compiledBookSource.get('header'):
        headers = compiledBookSource['header']
    else:
        headers = ''
    urlObj = parseUrl(url, evalJs, headers=headers)
    if ruleContent.get('webJs'):
        urlObj['webJs'] = ruleContent['webJs']
    evalJs.set('baseUrl', url)
    content, __ = getContent(urlObj)
    return parseContent(compiledBookSource, urlObj, content.strip(), evalJs, nextChapterUrl=nextChapterUrl)


def parseContent(bS, urlObj, content, evalJs, **kwargs):
    ruleContent = bS['ruleContent']
    nextChapterUrl = kwargs.get('nextChapterUrl')
    # if not ruleContent:
    #     return {}

    _content = content

    if content and content.startswith('<') and content.endswith('>'):
        try:
            content = parse(content, sanitize_names=False)
        except Exception:
            content = HTML(content)
    elif content and content.startswith('{') and content.endswith('}'):
        content = json.loads(content)

    chapterContent = {'content': ''}

    def parseCt(content):

        if ruleContent.get('content'):
            chapterContent['content'] += getString(
                content, ruleContent['content'], evalJs, rawContent=_content)
            chapterContent['content'] += '\n'
        if ruleContent.get('nextContentUrl'):
            nextContentUrls = getStrings(
                content, ruleContent['nextContentUrl'], evalJs, rawContent=_content)
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
                urlObj = parseUrl(nextUrl, evalJs, urlObj['finalurl'])
                content, __ = getContent(urlObj)
                nextContentUrls = parseCt(content)
                if nextContentUrls:
                    nextUrl = urljoin(urlObj['url'], nextContentUrls[0])
                else:
                    break
        else:
            contents = fetchContents(nextContentUrls, urlObj)
            for content, __ in contents:
                parseCt(content)

    if chapterContent['content']:
        chapterContent['content'] = Fmt.html(chapterContent['content'])

    if ruleContent.get('replaceRegex'):
        chapterContent['content'] = getString(
            chapterContent['content'], ruleContent['replaceRegex'], evalJs, rawContent=_content)
    try:
        if checkPUA(chapterContent['content']):
            if DEBUG_MODE:
                print('parseContent 发现PUA字符，尝试OCR修复')
            PUAChars = collectPUAChars(chapterContent['content'])
            chapterContent['content'] = fixPUAStr(
                chapterContent['content'], urlObj['allFontFaceUrl'], PUAChars)
    except NameError:
        pass
    except Exception:
        if DEBUG_MODE:
            print('parseContent OCR修复出错，已取消进行')

    return chapterContent


def fetchContents(urls, urlObject):
    evalJs = EvalJs({})
    executor = ThreadPoolExecutor(max_workers=8)
    tasks = []
    results = []
    for u in urls:
        urlObj = parseUrl(u, evalJs, urlObject['finalurl'])
        task = executor.submit(getContent, urlObj)
        tasks.append(task)
    for task in tasks:
        results.append(task.result())
