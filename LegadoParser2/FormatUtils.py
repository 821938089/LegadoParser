import re
import unicodedata


class Fmt():
    bookNameRegex = re.compile(r'\s+作\s*者.*|\s+\S+\s+著')
    authorRegex = re.compile(r'^\s*作\s*者[:：\s]+|\s+著')
    spaceRegex = re.compile(r'&nbsp;|&ensp;|&emsp;')
    noPrintRegex = re.compile(r'&thinsp;|&zwnj;|&zwj;')
    wrapHtmlRegex = re.compile(r'</?(?:div|p|br|hr|h\d|article|dd|dl)[^>]*>')
    commentRegex = re.compile(r'<!--[^>]*-->')
    indent1Regex = re.compile(r'\s*\n+\s*')  # 段缩进正则1
    indent2Regex = re.compile(r'^[\n\s]+')  # 段缩进正则2
    lastRegex = re.compile(r'[\n\s]+$')  # 清理尾部空行
    otherHtmlRegex = re.compile(r'</?[a-zA-Z]+(?=[ >])[^<>]*>')
    scriptStyleRegex = re.compile(r'<script[^>]*>[\s\S]*?<\/script>|<style[^>]*>[\s\S]*?<\/style>')

    @classmethod
    def bookName(cls, text):
        return cls.bookNameRegex.sub('', text).strip()

    @classmethod
    def author(cls, text):
        return cls.authorRegex.sub('', text).strip()

    @classmethod
    def wordCount(cls, text):
        if not text:
            return ''
        try:
            words = int(text)
            if words > 10000:
                result = f'{words/10000.0:.1f}万字'
            else:
                result = f'{words}字'
        except:
            result = text

        return result

    @classmethod
    def html(cls, text, otherRegex=otherHtmlRegex):
        text = unicodedata.normalize('NFC', text)
        text = text.replace(u'\ufeff', '')
        text = cls.spaceRegex.sub(' ', text)
        text = cls.noPrintRegex.sub('', text)
        text = cls.wrapHtmlRegex.sub('\n', text)
        text = cls.commentRegex.sub('', text)
        text = otherRegex.sub('', text)
        text = cls.indent1Regex.sub('\n　　', text)
        text = cls.indent2Regex.sub('　　', text)
        text = cls.lastRegex.sub('', text)

        return text
