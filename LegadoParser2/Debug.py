import json
from LegadoParser2.Search import search
from LegadoParser2.BookInfo import getBookInfo
from LegadoParser2.ChapterList import getChapterList
from LegadoParser2.Chapter import getChapterContent
from LegadoParser2.exceptions import RuleNotSupportError, RuleCompileError
from httpx._exceptions import RequestError, HTTPStatusError
from cssselect.xpath import ExpressionError
from quickjs import JSException
import os
import traceback


def debug(bookSources, startName=''):
    start = False
    for bookSource in bookSources:
        if startName:
            if bookSource['bookSourceName'] == startName and not start:
                start = True
            if not start:
                continue
        print(f"当前书源：{bookSource['bookSourceName']}")
        bookSourcePath = f"./debug/{bookSource['bookSourceName']}"
        if not os.path.exists(bookSourcePath):
            os.mkdir(bookSourcePath)
        searchResult = bookInfo = chapterList = bookContent = ''
        try:
            searchResult = search(bookSource, '我的')
            if searchResult:
                bookInfo = getBookInfo(bookSource, searchResult[0]['bookUrl'])
            else:
                bookInfo = {}
            if bookInfo:
                chapterList = getChapterList(bookSource, bookInfo['tocUrl'])
            else:
                chapterList = []
            if chapterList and len(chapterList) > 2:
                bookContent = getChapterContent(
                    bookSource, chapterList[0]['url'], chapterList[1]['url'])
            elif chapterList:
                bookContent = getChapterContent(
                    bookSource, chapterList[0]['url'], chapterList[1]['url'])
            else:
                bookContent = {}
        except RuleNotSupportError as e:
            print(f'发生了异常 {e}')
        except RequestError as e:
            print(f'发生了异常 {e}')
        except NotImplementedError as e:
            print(f'发生了异常 {e}')
        except ExpressionError as e:
            print(f'发生了异常 {e}')
        except JSException as e:
            # 'TypeError: not a function'
            print(f'发生了异常 {e}')
            if "ReferenceError: 'JavaImporter' is not defined" in e.args[0]:
                pass
            elif "TypeError: not a function" in e.args[0]:
                pass
            elif "ReferenceError: 'org' is not defined" in e.args[0]:
                pass
            # else:
            #     raise
        except RuleCompileError as e:
            print(f'发生了异常 {e}')
        except HTTPStatusError as e:
            print(f'发生了异常 {e}')
        except Exception as e:
            print(f'发生了异常 {e}')
            with open(f'{bookSourcePath}/exception.txt', 'w', encoding='utf-8') as f:
                f.write(traceback.format_exc())
        with open(f'{bookSourcePath}/search.txt', 'w', encoding='utf-8') as f:
            f.write(json.dumps(searchResult, ensure_ascii=False, indent=4, sort_keys=True))
        with open(f'{bookSourcePath}/bookInfo.txt', 'w', encoding='utf-8') as f:
            f.write(json.dumps(bookInfo, ensure_ascii=False, indent=4, sort_keys=True))
        with open(f'{bookSourcePath}/chapterList.txt', 'w', encoding='utf-8') as f:
            f.write(json.dumps(chapterList, ensure_ascii=False, indent=4, sort_keys=True))
        with open(f'{bookSourcePath}/bookContent.txt', 'w', encoding='utf-8') as f:
            f.write(json.dumps(bookContent, ensure_ascii=False, indent=4, sort_keys=True))


if __name__ == '__main__':
    with open('bs2.txt', 'r', encoding='utf-8') as f:
        bookSources = json.loads(f.read())
        debug(bookSources)
