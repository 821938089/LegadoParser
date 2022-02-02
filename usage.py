from LegadoParser2 import search
from LegadoParser2 import getBookInfo
from LegadoParser2 import getChapterList
from LegadoParser2 import getChapterContent
import json
from pprint import pprint


def main():

    with open('booksource.txt', 'r', encoding='utf-8') as f:
        bookSource = json.loads(f.read())
    print('-' * 20 + '开始搜索' + '-' * 20)
    searchResult = search(bookSource, '我的')
    if searchResult:
        pprint(searchResult[0])
        print('-' * 20 + '开始获取详情' + '-' * 20)
        bookInfo = getBookInfo(bookSource, searchResult[0]['bookUrl'])
    else:
        bookInfo = {}
    if bookInfo:
        pprint(bookInfo)
        print('-' * 20 + '开始获取章节列表' + '-' * 20)
        chapterList = getChapterList(bookSource, bookInfo['tocUrl'])
        print(f'列表大小{len(chapterList)}')
    else:
        chapterList = []
    if chapterList and len(chapterList) > 2:

        pprint(chapterList[:3])
        print('-' * 20 + '开始获取内容' + '-' * 20)
        bookContent = getChapterContent(
            bookSource, chapterList[0]['url'], chapterList[1]['url'])
    elif chapterList:
        pprint(chapterList)
        print('-' * 20 + '开始获取内容' + '-' * 20)
        bookContent = getChapterContent(
            bookSource, chapterList[0]['url'], chapterList[1]['url'])
    else:
        print('-' * 20 + '开始获取内容' + '-' * 20)
        bookContent = {}
    if bookContent:
        pprint(bookContent)
    print('-' * 20 + '结束' + '-' * 20)


if __name__ == '__main__':
    main()
