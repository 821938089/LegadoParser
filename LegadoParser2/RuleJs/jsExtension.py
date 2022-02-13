from LegadoParser2.HttpRequset2 import req
from LegadoParser2.config import USER_AGENT, DEBUG_MODE
from fs.memoryfs import MemoryFS
from fs.zipfs import ZipFS
from charset_normalizer import from_bytes
from LegadoParser2.RulePacket import getRuleObj
from LegadoParser2.RuleEval import getString, getStrings


def getZipStringContent(url, path):
    if DEBUG_MODE:
        print(f'getZipStringContent called url:{url} path:{path}')
    headers = {'User-Agent': USER_AGENT}
    mem_fs = MemoryFS()
    with mem_fs.open('book.zip', 'wb+') as mem_zip_file:
        try:
            req(url, header=headers, file_obj=mem_zip_file)
        except:
            if DEBUG_MODE:
                print('getZipStringContent 文件下载失败')
            return ''
        if mem_zip_file.tell() > 0:
            zip_fs = ZipFS(mem_zip_file)
            if zip_fs.exists(path):
                with zip_fs.open(path, 'rb') as file:
                    text = str(from_bytes(file.read()).best())
                    return text
            else:
                if DEBUG_MODE:
                    print(f'getZipStringContent 压缩包内不存在此文件 path:{path}')
                return ''
        else:
            if DEBUG_MODE:
                print('getZipStringContent 压缩包为空')
            return ''


_cache = {}
_MAXCACHE = 512


def getStringJs(content, evalJs, rule, isUrl=False):
    rulesObj = None
    try:
        rulesObj = _cache[rule]
    except KeyError:
        pass
    if not rulesObj:
        rulesObj = getRuleObj(rule)
        if len(_cache) >= _MAXCACHE:
            # 删除最旧的缓存
            try:
                del _cache[next(iter(_cache))]
            except (StopIteration, RuntimeError, KeyError):
                pass
        _cache[rule] = rulesObj
    if isUrl:
        texts = getStrings(content, rulesObj, evalJs)
        if texts:
            return texts[0]
        else:
            return ''
    else:
        text = getString(content, rulesObj, evalJs)
        return text
