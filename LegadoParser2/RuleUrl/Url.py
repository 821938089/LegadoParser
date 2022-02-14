import json
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

from LegadoParser2 import GSON
from LegadoParser2.HttpRequset2 import req
from LegadoParser2.RuleType import RuleType
from LegadoParser2.RuleUrl.BodyType import Body
from LegadoParser2.RuleUrl.UrlEval import getUrlRuleObj, getString
from LegadoParser2.webview import WebView
from LegadoParser2.config import DEBUG_MODE, USER_AGENT


def parseUrl(ruleUrl, evalJs, baseUrl='', headers=''):
    urlObj = {
        'url': '',
        'method': 'GET',
        'body': '',
        'headers': {},
        'bodytype': None,
        'webView': False,
        'webJs': '',
        'allFontFaceUrl': None
    }
    bodyType = None
    ruleObj = getUrlRuleObj(ruleUrl)

    if len(ruleObj) == 1 and ruleObj[0]['type'] != RuleType.DefaultOrEnd:
        _url = getString(ruleUrl, getUrlRuleObj(ruleUrl), evalJs)
    else:
        _url = ruleUrl

    splitResult = _url.split(',', maxsplit=1)
    if len(splitResult) == 2 and splitResult[1].strip().startswith('{') and splitResult[1].strip().endswith('}'):
        url, options = splitResult

        url = urljoin(baseUrl, url)

        urlObj.update(GSON.parse(options))

        if isinstance(urlObj['headers'], str):
            urlObj['headers'] = GSON.parse(urlObj['headers'])

        if headers:
            try:
                urlObj['headers'].update(GSON.parse(headers))
            except:
                pass

        if isinstance(urlObj['body'], dict):
            urlObj['body'] = json.dumps(urlObj['body'])

        if urlObj['method'].upper() == 'POST':
            if urlObj['body'].startswith('{') and urlObj['body'].endswith('}'):
                bodyType = Body.JSON
            elif urlObj['body'].startswith('<') and urlObj['body'].endswith('>'):
                bodyType = Body.XML
            else:
                bodyType = Body.FORM

            urlObj['bodytype'] = bodyType

    else:
        # https://www.biquge.win/search.php?q={{key}}&p={{page}}
        # url = urljoin(baseUrl, searchUrl, allow_fragments=False)
        if headers:
            try:
                urlObj['headers'].update(GSON.parse(headers))
            except:
                pass
        url = urljoin(baseUrl, _url)
    urlObj['url'] = url
    setDefaultHeaders(urlObj['headers'], bodyType)
    if not urlObj.get('charset', None):
        urlObj['charset'] = 'utf-8'

    return urlObj


def setDefaultHeaders(headers, bodyType):
    headerKeys = [k.lower() for k in headers.keys()]
    if 'user-agent' not in headerKeys:
        headers['User-Agent'] = USER_AGENT
    if 'content-type' not in headerKeys:
        if bodyType == Body.FORM:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif bodyType == Body.JSON:
            headers['Content-Type'] = 'application/json'
        elif bodyType == Body.XML:
            headers['Content-Type'] = 'text/xml'


def urljoin(base, url):
    # HttpCon = getLeftStr(base, '://')
    # AddRoot = getMiddleStr(base, '://', '/')
    if url.startswith('http'):
        return url
    HttpCon, AddRoot = base.split('://')
    AddRoot = AddRoot.split('/')[0]
    if url[:2] == '//':
        return HttpCon + ':' + url
    elif url[:1] == '/':
        return HttpCon + '://' + AddRoot + url
    else:
        pos = base.rfind('/')
        return base[:pos + 1] + url


def getContent(urlObj):
    if urlObj['method'] == 'GET':
        method = 0
    elif urlObj['method'] == 'POST':
        method = 1
    redirected = False
    charset = urlObj['charset']
    bodyType = urlObj['bodytype']
    body = urlObj['body']
    url = urlparse(urlObj['url'])
    url = url._replace(query=urlencode(
        parse_qs(url.query, keep_blank_values=True), doseq=True, encoding=charset))
    url = urlunparse(url)
    userAgent = urlObj['headers']['User-Agent']
    respone = None

    if urlObj['webView'] and urlObj['method'] == 'GET':
        webView = WebView(userAgent)
        content = webView.getResponseByUrl(url, urlObj['webJs'])
        urlObj['allFontFaceUrl'] = webView.allFontFaceUrl
    elif urlObj['webView'] and urlObj['method'] == 'POST' and bodyType == Body.FORM:
        webView = WebView(userAgent)
        content = webView.getResponseByPost(url, body, charset, urlObj['webJs'])
        urlObj['allFontFaceUrl'] = webView.allFontFaceUrl
    else:
        if body and bodyType == Body.FORM:
            body = urlencode(parse_qs(body, keep_blank_values=True), doseq=True, encoding=charset)
        elif body:
            body = body.encode(charset)
        content, __, respone = req(url, header=urlObj['headers'],
                                   method=method, post_data=body)

    if respone:
        urlObj['finalurl'] = str(respone.url)
    else:
        urlObj['finalurl'] = url

    if urlObj['allFontFaceUrl']:
        for fontFaceUrl in urlObj['allFontFaceUrl']:
            if 'srcList' in fontFaceUrl:
                for urlDict in fontFaceUrl['srcList']:
                    urlDict['url'] = urljoin(urlObj['finalurl'], urlDict['url'])

    if respone and respone.history:
        urlObj['redirected'] = True
    else:
        urlObj['redirected'] = False

    # print(respone.status_code)
    # print(searchObj)
    if DEBUG_MODE:
        if respone:
            respone.raise_for_status()
    # if respone.status_code != 200:
    #     raise RequestError('状态码非200')
    # 重定向到了详情页
    if respone and respone.history:
        redirected = True
        return content, redirected
    else:
        return content, redirected
