from LegadoParser2.RuleUrl.Url import parseUrl, getContent, urljoin
from LegadoParser2.RuleJs.JS import EvalJs
from LegadoParser2.RulePacket import getRuleObj, trimBookSource
from LegadoParser2.RuleEval import getElements, getString, getStrings
from LegadoParser2.utils import validateFlag
from concurrent.futures import ThreadPoolExecutor


# from lxml.etree import HTML

def getChapterList(bS, url):
    trimBookSource(bS)
    evalJs = EvalJs(bS)
    if bS.get('header', None):
        headers = bS['header']
    else:
        headers = ''
    urlObj = parseUrl(url, evalJs, headers=headers)
    evalJs.set('baseUrl', url)
    content, __ = getContent(urlObj)
    return parseChapterList(bS, urlObj, content.strip(), evalJs)


def parseChapterList(bS, urlObj, content, evalJs):
    ruleToc = bS['ruleToc']

    if not ruleToc:
        return []
    if ruleToc.get('chapterList', None):
        rulesChapterList = getRuleObj(ruleToc['chapterList'])
    if ruleToc.get('chapterName', None):
        rulesChapterName = getRuleObj(ruleToc['chapterName'])
    if ruleToc.get('chapterUrl', None):
        rulesChapterUrl = getRuleObj(ruleToc['chapterUrl'])
    if ruleToc.get('isPay', None):
        rulesIsPay = getRuleObj(ruleToc['isPay'])
    if ruleToc.get('isVip', None):
        rulesIsVip = getRuleObj(ruleToc['isVip'])
    if ruleToc.get('isVolume', None):
        rulesIsVolume = getRuleObj(ruleToc['isVolume'])
    if ruleToc.get('nextTocUrl', None):
        rulesNextTocUrl = getRuleObj(ruleToc['nextTocUrl'])
    if ruleToc.get('updateTime', None):
        rulesUpdateTime = getRuleObj(ruleToc['updateTime'])

    chapterList = []

    def parseCL(content):

        elements = getElements(content, rulesChapterList, evalJs)
        if ruleToc.get('nextTocUrl', None):
            nextTocUrls = getStrings(content, rulesNextTocUrl, evalJs)
        else:
            nextTocUrls = None
        for e in elements:
            chapter = {}
            if ruleToc.get('chapterName', None):
                chapter['name'] = getString(e, rulesChapterName, evalJs)
            if ruleToc.get('chapterUrl', None):
                chapter['url'] = getString(e, rulesChapterUrl, evalJs)
                if chapter['url']:
                    chapter['url'] = urljoin(urlObj['url'], chapter['url'])
            if ruleToc.get('isPay', None):
                chapter['isPay'] = getString(e, rulesIsPay, evalJs)
                chapter['isPay'] = validateFlag(chapter['isPay'])
            if ruleToc.get('isVip', None):
                chapter['isVip'] = getString(e, rulesIsVip, evalJs)
                chapter['isVip'] = validateFlag(chapter['isVip'])
            if ruleToc.get('isVolume', None):
                chapter['isVolume'] = getString(e, rulesIsVolume, evalJs)
                chapter['isVolume'] = validateFlag(chapter['isVolume'])
            if ruleToc.get('updateTime', None):
                chapter['updateTime'] = getString(e, rulesUpdateTime, evalJs)
            if chapter['name']:
                chapterList.append(chapter)

        return nextTocUrls

    nextTocUrls = parseCL(content)

    if nextTocUrls:
        if len(nextTocUrls) == 1:
            nextUrl = nextTocUrls[0]
            allNextUrls = []
            webViewSession = urlObj.get('webViewSession')
            while nextTocUrls and nextUrl not in allNextUrls:
                allNextUrls.append(nextUrl)
                urlObj = parseUrl(nextUrl, evalJs, urlObj['url'])
                urlObj['webViewSession'] = webViewSession
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
