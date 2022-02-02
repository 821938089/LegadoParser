from html5_parser import parse
from lxml.etree import tostring, HTML, tostringlist, HTMLParser
import re


def getStr(elements, tlst=[], regex=re.compile(r'\n\s*')):
    if elements.tag == 'br':
        tlst.append('\n')
    if elements.text:
        tlst.append(regex.sub('', elements.text))
    for e in elements:
        getStr(e)
    if elements.tail:
        tlst.append(regex.sub('', elements.tail))
    return ''.join(tlst)


with open('t.html', 'r', encoding='utf-8') as f:
    t = f.read()
    content = parse(t)
    # content = HTML(t, HTMLParser(remove_blank_text=True))
    a = content.cssselect("#htmlContent")

    # print(textlist)
    # print(''.join([i.strip() for i in textlist]))
    print(tostring(a[0], with_tail=False, method='html', prett, encoding='utf-8').decode())
