# LegadoParser

[阅读3.0](https://github.com/gedoor/legado)书源规则解析库

支持大多数 `Default` `Jsonpath` `Xpath` `Regex` 规则

支持部分 `Js` 规则

支持部分特殊规则，如 `{{ }}`、`{$. }`、正则替换

支持 `webView` ，使用Selenium驱动，需要安装[`Chrome`](https://www.google.cn/chrome/)浏览器

更多细节请查看[实现细节支持文档](https://github.com/821938089/LegadoParser/blob/main/ruleDoc.md)

Windows下需要Python 3.9版本，其他Python版本的部分依赖安装需要自行编译

调试模式开关在[config.py](https://github.com/821938089/LegadoParser/blob/main/LegadoParser2/config.py)中

## 安装

### Windows （Python 3.9）

```bash
git clone https://github.com/821938089/LegadoParser
cd LegadoParser
pip install -r requirements_win.txt
```

### Linux/WSL （Python 3.8+）

```bash
git clone https://github.com/821938089/LegadoParser
cd LegadoParser
sudo apt-get install libxml2 libxml2-dev
pip install -r requirements_linux.txt
```

### OCR可选安装

~~~bash
pip install -r requirements_ocr.txt
~~~

安装后使用webView获取章节内容会自动检测是否需要OCR

## 基础用法

详见 [`usage.py`](https://github.com/821938089/LegadoParser/blob/main/usage.py)

## 高级API

```python
from LegadoParser2.Search import search

def search(bS, key, page=1):
"""
搜索函数

参数 - 描述 - 类型

bS - 书源 - dict
key - 搜索 - str
page - 页数 - int

返回值 list[dict]

注意：如果搜索后直接跳转到了详情页，将调用parseBookInfo获取信息，字典key注意差异。
书籍Url的key将从bookUrl变为tocUrl。
"""
```

```python
from LegadoParser2.BookInfo import getBookInfo

def getBookInfo(bS, url):
"""
获取详情信息

参数 - 描述 - 类型

bS - 书源 - dict
url - search函数中返回的 bookUrl 或 tocUrl - str

"""
```

```python
from LegadoParser2.ChapterList import getChapterList

def getChapterList(bS, url):
"""
获取章节列表

参数 - 描述 - 类型

bS - 书源 - dict
url - getBookInfo函数中返回的tocUrl - str

"""
```

```python
from LegadoParser2.Chapter import getChapterContent

def getChapterContent(bS, url, nextChapterUrl=''):
"""
获取章节内容

参数 - 描述 - 类型

bS - 书源 - dict
url - getChapterList函数中返回的url - str
nextChapterUrl - 下一章的url - str
"""
```

```python
from LegadoParser2.RuleEval import getElements, getString, getStrings
from LegadoParser2.RulePacket import getRuleObj

# 基础API
```

## 示例结果

```python
--------------------开始搜索--------------------
{'author': '遥的海王琴',
 'bookUrl': 'https://www.zhaishuyuan.org/book/9/9256/',
 'coverUrl': 'https://img.zhaishuyuan.org/9/9256/9256s.jpg',
 'intro': '方瑾凌刚醒过来的时候，正好听到云阳侯将外室接了回来，据说私生子分外出息，欢欢喜喜地准备认祖归宗。府里上下都觉得云阳侯要舍弃活不长久的嫡子，培养庶子，等着看云阳侯夫人和方瑾
凌的笑话。然而云阳侯夫人却守在方瑾凌身边，放下一句：“凌儿，娘想和离。”云阳侯只道他的夫人只是一句狠话，温柔贤惠的性子哪儿敢真走。可没想到，春节未过，西陵侯府来人敲开了大门，一字排开 
的尚家小姐们恭请小姑姑和小表弟回家。看着这一二三',
 'kind': '连载,其他,55分钟前',
 'lastChapter': '第194章 谋逆蛊惑太子悖逆人伦55分钟前',
 'name': '我的江山，你随便捏',
 'wordCount': '98字'}
--------------------开始获取详情--------------------
{'author': '遥的海王琴',
 'coverUrl': 'https://img.zhaishuyuan.org/9/9256/9256s.jpg',
 'intro': '\u3000\u3000'
          '方瑾凌刚醒过来的时候，正好听到云阳侯将外室接了回来，据说私生子分外出息，欢欢喜喜地准备认祖归宗。府里上下都觉得云阳侯要舍弃活不长久的嫡子，培养庶子，等着看云阳侯夫人和方瑾
凌的笑话。然而云阳侯夫人却守在方瑾凌身边，放下一句：“凌儿，娘想和离。”云阳侯只道他的夫人只是一句狠话，温柔贤惠的性子哪儿敢真走。可没想到，春节未过，西陵侯府来人敲开了大门，一字排开 
的尚家小姐们恭请小姑姑和小表弟回家。看着这一二三',
 'kind': '其他,连载,2022-02-02',
 'lastChapter': '',
 'name': '我的江山，你随便捏',
 'tocUrl': 'https://www.zhaishuyuan.org/book/9/9256/',
 'wordCount': '98 万字'}
--------------------开始获取章节列表--------------------
列表大小193
[{'name': '第1章 寒冬 ',
  'url': 'https://www.zhaishuyuan.org/book/9256/7423287.html'},
 {'name': '第2章 苏醒 ',
  'url': 'https://www.zhaishuyuan.org/book/9256/7423288.html'},
 {'name': '第3章 做戏 ',
  'url': 'https://www.zhaishuyuan.org/book/9256/7423289.html'}]
--------------------开始获取内容--------------------
略
--------------------结束--------------------
```
