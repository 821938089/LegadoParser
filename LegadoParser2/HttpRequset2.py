import httpx
from httpx._exceptions import CookieConflict
requests = None
currentProxies = ''

# post_data_type 一般用 1 这样post_data不会做url编码


# def log_request(request):
#     print(request.headers)


def req(url, cellphone_mode=False, cookies='', header={}, method=0, post_data_type=1, post_data='', post_json={}, return_cookies='', proxy='', proxy_type='', timeout=10, file_name='', file_obj=None, allow_redirects=True):
    global requests, currentProxies

    tmp_header = {}
    proxies = None
    tmp_cookies = {}
    tmp_post_data = {}

    if proxy and proxy_type:
        proxies = {}
        proxies[proxy_type] = proxy

        # print('设置了代理')
    elif proxy:
        proxies = proxy

    if requests == None:
        requests = httpx.Client(http2=True, proxies=proxies, verify=False)
        # requests.event_hooks['request'] = [log_request]
    elif currentProxies and currentProxies != proxy:
        requests.close()
        del requests
        # proxies = {}
        # proxies[proxy_type] = proxy
        requests = httpx.Client(http2=True, proxies=proxies, verify=False)
    currentProxies = proxy
    if 'User-Agent' in header and header['User-Agent'] != '':
        pass
    elif 'user-agent' in header and header['user-agent'] != '':
        pass
    else:
        if not cellphone_mode:
            tmp_header['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36'
        else:
            tmp_header['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

    tmp_header = dict(tmp_header, **header)
    if cookies:
        for line in cookies.split(';'):
            if line.strip() == '':
                continue

            name, value = line.strip().split('=', 1)
            tmp_cookies[name] = value
    # print(requests.cookies)
    requests.cookies = tmp_cookies

#    if post_data:
#        for line in post_data.split('&'):
#            name,value=line.strip().split('=',1)
#            tmp_post_data[name] = value

    if method == 0:  # get方式访问
        # print (tmp_cookies)
        if file_name == '' and not file_obj:
            r = requests.get(
                url, headers=tmp_header, timeout=timeout, follow_redirects=allow_redirects)
        else:
            with requests.stream('GET', url, headers=tmp_header,
                                 timeout=timeout, follow_redirects=allow_redirects) as r:
                r.raise_for_status()
                if not file_obj:
                    with open(file_name, "wb") as file:
                        for chunk in r.iter_bytes(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                else:
                    for chunk in r.iter_bytes(chunk_size=1024):
                        if chunk:
                            file_obj.write(chunk)
            return
        # print (r.text)
    if method == 1:  # post方式访问
        if post_data and post_data_type == 0:
            for line in post_data.split('&'):
                # print (line)
                name, value = line.strip().split('=', 1)
                tmp_post_data[name] = value
        # print (tmp_post_data)

        if post_data_type == 0:
            r = requests.post(url, headers=tmp_header,
                              data=tmp_post_data, timeout=timeout, follow_redirects=allow_redirects)
        elif post_data_type == 1:
            # post内容不做url编码
            r = requests.post(url, headers=tmp_header,
                              data=post_data, timeout=timeout, follow_redirects=allow_redirects)
        else:
            r = requests.post(url, headers=tmp_header,
                              json=post_json, timeout=timeout, follow_redirects=allow_redirects)
    if file_name == '':
        tmp_return_cookies = r.cookies

        for tmp_a in tmp_return_cookies:
            try:
                return_cookies += tmp_a + "=" + tmp_return_cookies[tmp_a] + "; "
            except CookieConflict:
                pass

    if file_name == '':
        if r.encoding is None or r.encoding.lower() not in {'utf-8', 'gbk', 'gb2312'}:
            if r.content.find(b'charset=gbk') != -1 or r.content.find(b'charset=gb2312') != -1 or r.content.find(b'charset="gbk"') != -1:
                r.encoding = "gb18030"
            else:
                r.encoding = "utf-8"
        elif r.encoding == 'gb2312':
            r.encoding = 'gb18030'
    # print(r.http_version)
    # print(r.cookies)
    return r.text, return_cookies, r


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(filename="httpx.log", filemode="w", level=logging.NOTSET)

    pass
