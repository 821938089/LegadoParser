"""
书籍搜索


"""
from LegadoParser2.RuleJs.JS import EvalJs
from LegadoParser2.RuleEval import getElements, getStrings, getString
from LegadoParser2.RuleUrl.Url import parseUrl, getContent
from LegadoParser2.RuleUrl.BodyType import Body
from LegadoParser2.FormatUtils import Fmt
from LegadoParser2.BookInfo import parseBookInfo
from LegadoParser2.config import DEBUG_MODE
# from lxml.html import tostring
# from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
# from httpx._exceptions import RequestError
# from urllib.parse import urlparse


# ast.literal_eval 解析单引号的字典 https://stackoverflow.com/questions/4162642/single-vs-double-quotes-in-json
# 参数 bS:bookSource 单个书源规则json dict类型

# 搜索大致流程：
# 1、统一搜索Url的结构
# 2、发送请求获取Html/Json
# 3、通过规则解析获取统一结构的书籍搜索数据


def search(compiledBookSource, key, page=1):
    # trimBookSource(bS)
    evalJS = EvalJs(compiledBookSource)
    searchObj = parseSearchUrl(compiledBookSource, key, page, evalJS)
    content, redirected = getContent(searchObj)

    return getSearchResult(compiledBookSource, searchObj, content, evalJS)


def parseSearchUrl(bS, key, page, evalJs):
    # 统一搜索Url的结构
    # searchUrl类型有三种
    # https://www.biquge.win/search.php?q={{key}}&p={{page}}
    # https://www.imiaobige.com/search.html,{"method": "POST","body": "searchkey={{key}}"}
    # 还有一种是带js的
    searchUrl = bS['searchUrl']
    baseUrl = bS['bookSourceUrl']
    # 删除链接中的fragment
    baseUrl = baseUrl.split('#', 1)[0]

    if bS.get('header', None):
        headers = bS['header']
    else:
        headers = ''

    evalJs.set('page', page)
    evalJs.set('key', key)

    searchObj = parseUrl(searchUrl, evalJs, baseUrl, headers)

    evalJs.set('baseUrl', searchObj['rawUrl'])
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


def getSearchResult(bS, urlObj, content, evalJs: EvalJs, **kwargs):
    ruleSearch = bS['ruleSearch']

    if not ruleSearch:
        return []

    redirected = urlObj['redirected']
    useWebView = urlObj['webView']

    elements = getElements(content, ruleSearch['bookList'], evalJs)

    if not elements and (redirected or useWebView):
        return [parseBookInfo(bS, urlObj, content, evalJs)]

    searchResult = []
    finalUrl = urlObj['finalurl']  # 最终访问的url，可能是跳转后的Url
    # finalUrl = urlparse(finalUrl)._replace(query='').geturl()  # 去除query

    for e in elements:

        bookInfo = {}
        # if DEBUG_MODE:
        #     ehtml = tostring(e, encoding='utf-8').decode()
        try:
            bookInfo['name'] = Fmt.bookName(getString(e, ruleSearch['name'], evalJs).strip())
            bookUrlList = getStrings(e, ruleSearch['bookUrl'], evalJs)
            if bookUrlList:
                bookInfo['bookUrl'] = urljoin(finalUrl, bookUrlList[0].strip())
            else:
                bookInfo['bookUrl'] = urlObj['rawUrl']
            if ruleSearch.get('author', None):
                bookInfo['author'] = Fmt.author(getString(e, ruleSearch['author'], evalJs).strip())
            if ruleSearch.get('kind', None):
                bookInfo['kind'] = ','.join(getStrings(e, ruleSearch['kind'], evalJs)).strip()
            if ruleSearch.get('coverUrl', None):
                bookInfo['coverUrl'] = urljoin(finalUrl,
                                               getString(e, ruleSearch['coverUrl'], evalJs).strip())
            if ruleSearch.get('wordCount', None):
                bookInfo['wordCount'] = Fmt.wordCount(
                    getString(e, ruleSearch['wordCount'], evalJs).strip())
            if ruleSearch.get('intro', None):
                bookInfo['intro'] = Fmt.html(getString(e, ruleSearch['intro'], evalJs).strip())
            if ruleSearch.get('lastChapter', None):
                bookInfo['lastChapter'] = getString(e, ruleSearch['lastChapter'], evalJs).strip()
            bookInfo['variables'] = evalJs.dumpVariables()
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
