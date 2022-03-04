from LegadoParser2.RuleUrl.Url import parseUrl, getContent, urljoin
from LegadoParser2.RuleJs.JS import EvalJs
from LegadoParser2.RuleEval import getElements, getString, getStrings
from LegadoParser2.utils import validateFlag
from concurrent.futures import ThreadPoolExecutor


# from lxml.etree import HTML

def getChapterList(compiledBookSource, url, variables):
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
    return parseChapterList(compiledBookSource, urlObj, content.strip(), evalJs)


def parseChapterList(bS, urlObj, content, evalJs: EvalJs):
    ruleToc = bS['ruleToc']

    # if not ruleToc:
    #     return []

    chapterList = []

    chapterUrlSet = set()

    def parseCL(content):

        elements = getElements(content, ruleToc['chapterList'], evalJs)

        for e in elements:
            chapter = {}
            if ruleToc.get('chapterName', None):
                chapter['name'] = getString(e, ruleToc['chapterName'], evalJs)
            if ruleToc.get('chapterUrl', None):
                chapter['url'] = getString(e, ruleToc['chapterUrl'], evalJs)
                if chapter['url']:
                    chapter['url'] = urljoin(urlObj['finalurl'], chapter['url'])
                else:
                    chapter['url'] = urlObj['rawUrl']
                chapterUrlSet.add(chapter['url'])
            else:
                chapter['url'] = urlObj['rawUrl']
            if not chapter.get('url'):
                chapter['url'] = urlObj['rawUrl']
            if ruleToc.get('isPay', None):
                chapter['isPay'] = getString(e, ruleToc['isPay'], evalJs)
                chapter['isPay'] = validateFlag(chapter['isPay'])
            if ruleToc.get('isVip', None):
                chapter['isVip'] = getString(e, ruleToc['isVip'], evalJs)
                chapter['isVip'] = validateFlag(chapter['isVip'])
            if ruleToc.get('isVolume', None):
                chapter['isVolume'] = getString(e, ruleToc['isVolume'], evalJs)
                chapter['isVolume'] = validateFlag(chapter['isVolume'])
            if ruleToc.get('updateTime', None):
                chapter['updateTime'] = getString(e, ruleToc['updateTime'], evalJs)
            chapter['variables'] = evalJs.dumpVariables()
            if chapter['name']:
                chapterList.append(chapter)

        if ruleToc.get('nextTocUrl', None):
            nextTocUrls = getStrings(content, ruleToc['nextTocUrl'], evalJs)
            if nextTocUrls:
                nextTocUrls = [nextTocUrl for nextTocUrl in nextTocUrls if urljoin(
                    urlObj['finalurl'], nextTocUrl) not in chapterUrlSet]
        else:
            nextTocUrls = None

        return nextTocUrls

    nextTocUrls = parseCL(content)

    if nextTocUrls:
        if len(nextTocUrls) == 1:
            nextUrl = nextTocUrls[0]
            allNextUrls = []
            while nextTocUrls and nextUrl not in allNextUrls:
                allNextUrls.append(nextUrl)
                urlObj = parseUrl(nextUrl, evalJs, urlObj['finalurl'])
                content, __ = getContent(urlObj)
                nextTocUrls = parseCL(content)
                if nextTocUrls:
                    nextUrl = nextTocUrls[0]
                else:
                    break
        else:
            contents = fetchContents(nextTocUrls, urlObj['url'])
            for content, __ in contents:
                parseCL(content)
    chapterList = removeLatestChapter(chapterList)

    return chapterList


def fetchContents(urls, baseUrl):
    evalJs = EvalJs({})
    executor = ThreadPoolExecutor(max_workers=8)
    tasks = []
    results = []
    for u in urls:
        urlObj = parseUrl(u, evalJs, baseUrl)
        task = executor.submit(getContent, urlObj)
        tasks.append(task)
    for task in tasks:
        results.append(task.result())
    return results


# 移除章节列表中上方的最新章节
def removeLatestChapter(chapterList):
    if not chapterList:
        return chapterList

    length = len(chapterList)
    for idx in range(length):
        if chapterList[idx]['url'] != chapterList[length - idx - 1]['url'] or idx + 1 > length / 2:
            break
    return chapterList[idx:]
