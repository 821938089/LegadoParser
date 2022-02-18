"""
书籍搜索


"""
from LegadoParser2.RuleJs.JS import EvalJs
from LegadoParser2.RuleEval import getElements, getStrings, getString
from LegadoParser2.RulePacket import getRuleObj, trimBookSource
from LegadoParser2.RuleUrl.Url import parseUrl, getContent
from LegadoParser2.RuleUrl.BodyType import Body
from LegadoParser2.FormatUtils import Fmt
from LegadoParser2.BookInfo import parseBookInfo
from LegadoParser2.config import DEBUG_MODE
# from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
# from httpx._exceptions import RequestError
# from urllib.parse import urlparse


# ast.literal_eval 解析单引号的字典 https://stackoverflow.com/questions/4162642/single-vs-double-quotes-in-json
# 参数 bS:bookSource 单个书源规则json dict类型

# 搜索大致流程：
# 1、统一搜索Url的结构
# 2、发送请求获取Html/Json
# 3、通过规则解析获取统一结构的书籍搜索数据


def search(bS, key, page=1):
    trimBookSource(bS)
    evalJS = EvalJs(bS)
    searchObj = parseSearchUrl(bS, key, page, evalJS)
    content, redirected = getContent(searchObj)
    # cProfile.runctx('getSearchResult(bS, searchObj, content)', globals(), locals(), 'program.prof')
    return getSearchResult(bS, searchObj, content, evalJS)


def parseSearchUrl(bS, key, page, evalJs):
    # 统一搜索Url的结构
    # searchUrl类型有三种
    # https://www.biquge.win/search.php?q={{key}}&p={{page}}
    # https://www.imiaobige.com/search.html,{"method": "POST","body": "searchkey={{key}}"}
    # 还有一种是带js的
    searchUrl = bS['searchUrl']
    baseUrl = bS['bookSourceUrl']
    if bS.get('header', None):
        headers = bS['header']
    else:
        headers = ''

    evalJs.set('page', page)
    evalJs.set('key', key)

    searchObj = parseUrl(searchUrl, evalJs, baseUrl, headers)

    evalJs.set('baseUrl', searchObj['url'])
    return searchObj


# def getContent(searchObj):
#     if searchObj['method'] == 'GET':
#         method = 0
#     elif searchObj['method'] == 'POST':
#         method = 1
#     redirected = False
#     charset = searchObj['charset']
#     bodyType = searchObj['bodytype']
#     body = searchObj['body']
#     url = urlparse(searchObj['url'])
#     url = url._replace(query=urlencode(parse_qs(url.query), doseq=True, encoding=charset))
#     url = urlunparse(url)
#     if body and bodyType == Body.FORM:
#         body = urlencode(parse_qs(body), doseq=True, encoding=charset)
#     elif body:
#         body = body.encode(charset)

#     content, __, respone = req(url, header=searchObj['headers'],
#                                method=method, post_data=body)
#     searchObj['finalurl'] = str(respone.url)
#     if respone.history:
#         searchObj['redirected'] = True
#     else:
#         searchObj['redirected'] = False

#     # print(respone.status_code)
#     # print(searchObj)
#     if respone.status_code != 200:
#         raise RequestError('状态码非200')
#     # 重定向到了详情页
#     if respone.history:
#         redirected = True
#         return content, redirected
#     else:
#         return content, redirected


def getSearchResult(bS, urlObj, content, evalJS, **kwargs):
    ruleSearch = bS['ruleSearch']
    if not ruleSearch:
        return []
    redirected = urlObj['redirected']
    useWebView = urlObj['webView']
    elements = getElements(content, getRuleObj(ruleSearch['bookList']), evalJS)

    if not elements and (redirected or useWebView):
        return [parseBookInfo(bS, urlObj, content, evalJS)]

    searchResult = []
    finalUrl = urlObj['finalurl']  # 最终访问的url，可能是跳转后的Url
    # finalUrl = urlparse(finalUrl)._replace(query='').geturl()  # 去除query

    rulesName = getRuleObj(ruleSearch['name'])
    rulesBookUrl = getRuleObj(ruleSearch['bookUrl'])
    if ruleSearch.get('author', None):
        rulesAuthor = getRuleObj(ruleSearch['author'])
    if ruleSearch.get('kind', None):
        rulesKind = getRuleObj(ruleSearch['kind'])
    if ruleSearch.get('coverUrl', None):
        rulesCoverUrl = getRuleObj(ruleSearch['coverUrl'])
    if ruleSearch.get('wordCount', None):
        rulesWordCount = getRuleObj(ruleSearch['wordCount'])
    if ruleSearch.get('intro', None):
        rulesIntro = getRuleObj(ruleSearch['intro'])
    if ruleSearch.get('lastChapter', None):
        rulesLastChapter = getRuleObj(ruleSearch['lastChapter'])

    for e in elements:

        bookInfo = {}
        try:
            bookInfo['name'] = Fmt.bookName(getString(e, rulesName, evalJS).strip())
            bookInfo['bookUrl'] = urljoin(finalUrl, getStrings(e, rulesBookUrl, evalJS)[0].strip())
            if ruleSearch.get('author', None):
                bookInfo['author'] = Fmt.author(getString(e, rulesAuthor, evalJS).strip())
            if ruleSearch.get('kind', None):
                bookInfo['kind'] = ','.join(getStrings(e, rulesKind, evalJS)).strip()
            if ruleSearch.get('coverUrl', None):
                bookInfo['coverUrl'] = urljoin(finalUrl,
                                               getString(e, rulesCoverUrl, evalJS).strip())
            if ruleSearch.get('wordCount', None):
                bookInfo['wordCount'] = Fmt.wordCount(getString(e, rulesWordCount, evalJS).strip())
            if ruleSearch.get('intro', None):
                bookInfo['intro'] = Fmt.html(getString(e, rulesIntro, evalJS).strip())
            if ruleSearch.get('lastChapter', None):
                bookInfo['lastChapter'] = getString(e, rulesLastChapter, evalJS).strip()

        except IndexError as e:
            if not len(searchResult):
                if DEBUG_MODE:
                    raise
            # else:
            #     print('部分书籍解析失败')
        else:
            searchResult.append(bookInfo)

    return searchResult


def setDefaultHeaders(headers, bodyType):
    headerKeys = [k.lower() for k in headers.keys()]
    if 'user-agent' not in headerKeys:
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    if 'content-type' not in headerKeys:
        if bodyType == Body.FORM:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif bodyType == Body.JSON:
            headers['Content-Type'] = 'application/json'


def urljoin(base, url):
    # HttpCon = getLeftStr(base, '://')
    # AddRoot = getMiddleStr(base, '://', '/')
    HttpCon, AddRoot = base.split('://')
    AddRoot = AddRoot.split('/')[0]
    if url[:4] == 'http':
        return url
    elif url[:2] == '//':
        return HttpCon + url
    elif url[:1] == '/':
        return HttpCon + '://' + AddRoot + url
    else:
        pos = base.rfind('/')
        return base[:pos] + url
