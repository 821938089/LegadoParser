import re
import base64

from LegadoParser2.config import DEBUG_MODE, USER_AGENT
from LegadoParser2.HttpRequset2 import req
from fs.memoryfs import MemoryFS
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from cnocr import CnOcr
from cnocr.utils import read_img
from LegadoParser2.StrOperate import getRightStr

# Private Use Areas 私人使用区 私人使用区 范围\ue000-\uf8ff
# https://zh.wikipedia.org/wiki/%E7%A7%81%E4%BA%BA%E4%BD%BF%E7%94%A8%E5%8C%BA
# 查看 unicode 区段 https://www.fileformat.info/info/unicode/block/index.htm
# https://www.cnblogs.com/geeksongs/p/14351576.html
# https://blog.harumonia.moe/font-antispider-cracker/
# https://seealso.cn/post/use-fonttools-build-webfont-to-anti-crawler/


def checkPUA(text):
    # 检查是否含有PUA字符

    PUARegex = re.compile(r'[\ue000-\uf8ff]')
    if PUARegex.search(text):
        return True
    else:
        return False


def collectPUAChars(text):
    # 收集所有PUA字符
    chars = []
    for i in text:
        if 0xe000 <= ord(i) <= 0xf8ff:
            chars.append(i)
    chars = list(set(chars))
    return chars


def woff2ttf(woffFile, ttfFile):
    # https://github.com/fonttools/fonttools/issues/1694
    font = TTFont(woffFile)
    font.flavor = None
    font.save(ttfFile)


def getFontUrl(allFontFaceUrl):
    # 获取支持的字体文件Url
    if not allFontFaceUrl:
        if DEBUG_MODE:
            print('getFontUrl allFontFaceUrl为None')
        return ''
    for fontFaceUrl in allFontFaceUrl:
        if 'srcList' in fontFaceUrl:
            for urlDict in fontFaceUrl['srcList']:
                if not urlDict['format']:
                    if urlDict['url'].find('.ttf') != -1 or urlDict['url'].find('.woff') != -1 or urlDict['url'].find('.woff2') != -1:
                        return urlDict['url']
                elif urlDict['format'] in {'woff', 'woff2', 'truetype', 'opentype'}:
                    return urlDict['url']
    return ''


def checkCharInFont(uniChar, font):
    # 检查字符是否在字体文件中
    # https://stackoverflow.com/questions/43834362/python-unicode-rendering-how-to-know-if-a-unicode-character-is-missing-from-the
    for cmap in font['cmap'].tables:
        if cmap.isUnicode():
            if ord(uniChar) in cmap.cmap:
                return True
    return False


def writeFontPng(char, font, fontSize, mem_fs):
    # 将字体转换为图片写入到内存中
    # https://clay-atlas.com/us/blog/2020/08/26/use-python-pacakge-pillow-to-convert-font-files-to-png-images/
    # https://pillow.readthedocs.io/en/stable/reference/ImageFont.html

    codePoint = ord(char)
    W, H = (fontSize + 12, fontSize + 12)  # 合适的文字与背景大小比例可提高识别成功率
    image = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(image)
    offset_w, offset_h = font.getoffset(char)
    w, h = draw.textsize(char, font=font)
    pos = ((W - w - offset_w) / 2, (H - h - offset_h) / 2)

    draw.text(pos, char, "black", font=font)

    with mem_fs.open(f'{codePoint}.png', 'wb+') as png_file:
        image.save(png_file, format='png')
        # image.save(f'{codePoint}.png', format='png')


def ocrFont(PUAChars, fontFile, mem_fs):
    # 调用OCR识别图片中的文字
    # 返回字符转换字典
    # 备选OCR识别库 paddleocr
    # https://zhuanlan.zhihu.com/p/342686109 看评论区
    # https://cnocr.readthedocs.io/zh/latest/usage/
    # https://github.com/breezedeus/cnocr
    # https://pillow.readthedocs.io/en/stable/reference/ImageFont.html
    fontSize = 28  # 字体大小
    fontFile.seek(0)
    font = ImageFont.truetype(fontFile, fontSize)
    ocr = CnOcr()
    charDict = {}
    for char in PUAChars:
        writeFontPng(char, font, fontSize, mem_fs)
    for char in PUAChars:
        codePoint = ord(char)
        with mem_fs.open(f'{codePoint}.png', 'rb') as png_file:
            res = ocr.ocr_for_single_line(read_img(png_file))
            if res:
                charDict[char] = res[0][0][0]
            else:
                charDict[char] = char
    return charDict


def fixPUAStr(text, allFontFaceUrl, PUAChars):
    # 主函数
    # 修复错误字符
    fontUrl = getFontUrl(allFontFaceUrl)

    if not fontUrl:
        if DEBUG_MODE:
            print('fixPUAStr 未找到可以解析的字体')
        return text

    headers = {'User-Agent': USER_AGENT}
    mem_fs = MemoryFS()
    with mem_fs.open('font', 'wb+') as mem_font_file:
        try:
            if fontUrl.startswith('data:'):
                fontbs64 = getRightStr(fontUrl, 'base64,')
                mem_font_file.write(base64.b64decode(fontbs64))
            else:
                req(fontUrl, header=headers, file_obj=mem_font_file)
        except:
            if DEBUG_MODE:
                print('fixPUAStr 字体文件下载失败')
            return text
        if mem_font_file.tell() > 0:
            # https://stackoverflow.com/questions/43834362/python-unicode-rendering-how-to-know-if-a-unicode-character-is-missing-from-the
            # https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
            font = TTFont(mem_font_file)
            if font.flavor in {'woff', 'woff2'}:
                # 转换 woff woff2 到 ttf
                # https://github.com/fonttools/fonttools/issues/1694
                font.flavor = None
                mem_font_file.truncate(0)
                mem_font_file.seek(0)
                font.save(mem_font_file)

            PUAChars = list(filter(lambda x: checkCharInFont(x, font), PUAChars))
            if not PUAChars:
                if DEBUG_MODE:
                    print('fixPUAStr 字体文件中未找到可以替换的字')
                return text
            charDict = ocrFont(PUAChars, mem_font_file, mem_fs)
            for old, new in charDict.items():
                text = text.replace(old, new)
            return text

        else:
            if DEBUG_MODE:
                print('fixPUAStr 字体文件为空')
            return text


# 该js函数使用selenium在浏览器中执行，获取到的数据会保存到webView.allFontFaceUrl -> urlObj['allFontFaceUrl']
# 函数功能：获取同源css中的所有@font-face中的src
# 注意只有同源的css能获取到字体文件地址，非同源（cdn）的css无法获取字体地址，会返回css的href，没写这里的处理代码
# https://stackoverflow.com/questions/10248100/enumerate-font-face-urls-using-javascript-jquery
# https://www.paulirish.com/2009/font-face-feature-detection/
# https://developer.mozilla.org/zh-CN/docs/Web/CSS/@font-face
getAllFontFaceUrl = \
    '''function getAllFontFaceUrl() {
    let fontFaceList = []
    for (const styleSheet of document.styleSheets) {
        try {
            for (const cssRule of styleSheet.cssRules) {
                if (cssRule instanceof CSSFontFaceRule) {
                    let srcList = []
                    fontFamily = cssRule.style.fontFamily
                    src = cssRule.style.src
                    urlRegex =
                        /url\(["']{0,1}(.*?)["']{0,1}\)\s*format\(["'](.*?)["']\)|url\(["']{0,1}(.*?)["']{0,1}\)/g
                    if (src) {
                        for (const match of src.matchAll(urlRegex)) {
                            let srcObj
                            if (match[1]) {
                                srcObj = { url: match[1], format: match[2] }
                            } else {
                                srcObj = { url: match[3], format: null }
                            }
                            srcList.push(srcObj)
                        }
                    }
                    if (!fontFaceList.find(o => o.fontFamily === fontFamily)) {
                        fontFaceList.push({ fontFamily, srcList })
                    }
                }
            }
        } catch (e) {
            fontFaceList.push({ href: styleSheet.href })
        }
    }
    return fontFaceList
}
return getAllFontFaceUrl()
'''
