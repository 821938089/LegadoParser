from LegadoParser2.Search import search
from LegadoParser2.BookInfo import getBookInfo
from LegadoParser2.ChapterList import getChapterList
from LegadoParser2.Chapter import getChapterContent
from LegadoParser2.RuleCompile import compileBookSource
from pprint import pprint
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')


def main():

    with open('booksource.txt', 'r', encoding='utf-8') as f:
        bookSource = json.loads(f.read())
    compiledBookSource = compileBookSource(bookSource)
    print('-' * 20 + '开始搜索' + '-' * 20)
    searchResult = search(compiledBookSource, '我的')
    if searchResult:
        pprint(searchResult[0])
        print('-' * 20 + '开始获取详情' + '-' * 20)
        variables = searchResult[0]['variables']
        bookInfo = getBookInfo(compiledBookSource, searchResult[0]['bookUrl'], variables)
    else:
        bookInfo = {}
    if bookInfo:
        pprint(bookInfo)
        print('-' * 20 + '开始获取章节列表' + '-' * 20)
        variables = bookInfo['variables']
        chapterList = getChapterList(compiledBookSource, bookInfo['tocUrl'], variables)
        print(f'列表大小{len(chapterList)}')
    else:
        chapterList = []
    if chapterList and len(chapterList) >= 2:

        pprint(chapterList[:3])
        print('-' * 20 + '开始获取内容' + '-' * 20)
        variables = chapterList[0]['variables']
        bookContent = getChapterContent(
            compiledBookSource, chapterList[0]['url'], variables, chapterList[1]['url'])
    elif chapterList:
        pprint(chapterList)
        print('-' * 20 + '开始获取内容' + '-' * 20)
        variables = chapterList[0]['variables']
        bookContent = getChapterContent(
            compiledBookSource, chapterList[0]['url'], variables)
    else:
        print('-' * 20 + '开始获取内容' + '-' * 20)
        bookContent = {}
    if bookContent:
        pprint(bookContent)
    print('-' * 20 + '结束' + '-' * 20)


if __name__ == '__main__':
    main()
