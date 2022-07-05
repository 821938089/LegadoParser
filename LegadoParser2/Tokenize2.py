"""
https://segmentfault.com/a/1190000023133326

Legado 书源解析 词法分析 Lexical analyzer

"""
# from copy import deepcopy

"""
阅读3.0规则分词器

参数:
    text: 进行分词的规则

返回值:
    一个list里面按分词顺序存语法单元

    例如:['id.info', '@', 'tag.a.-1', '@', 'text', '&&', 'id.info',
        '@', 'tag.p.-2', '@', 'text', '##', '最后更新.|..\\:.*']

"""

# 参考
# 简单js编译器
# https://xiaodang.github.io/2020/10/27/%E7%94%A8JavaScript%E5%AE%9E%E7%8E%B0%E4%B8%80%E4%B8%AA%E7%AE%80%E5%8D%95%E7%9A%84%E7%BC%96%E8%AF%91%E5%99%A8/
# js执行
# https://github.com/PetterS/quickjs


from typing import List


def tokenizer(text: str) -> List[str]:
    """
    阅读3.0规则分词器

    参数:
        text: 进行分词的规则

    返回值:
        一个list里面按分词顺序存语法单元

        例如:['id.info', '@', 'tag.a.-1', '@', 'text', '&&', 'id.info',
            '@', 'tag.p.-2', '@', 'text', '##', '最后更新.|..\\:.*']
    """

    tokenList: List[str] = []
    stack: List[str] = []
    cursor = 0
    length = len(text)
    tmpStr = ""
    char = ""
    ck = Check(text, stack, tokenList).ck
    while cursor < length:
        char = text[cursor]
        tmpStr += char
        if char == "@":
            if (result := ck(cursor, tmpStr[:-1], "@get:{", "@get:{"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "{":
                        stack.append("{")
                        cursor += 1
                    elif char == "}":
                        if stack and stack[-1] == "{":
                            stack.pop()
                            cursor += 1
                        elif stack[-1] == "@get:{":
                            stack.pop()
                            tokenList.append(tmpStr[:-1])
                            tokenList.append("}")
                            cursor += 1
                            tmpStr = ""
                            break
                    else:
                        cursor += 1
            elif (result := ck(cursor, tmpStr[:-1], "@put:{", "@put:{"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "{":
                        stack.append("{")
                        cursor += 1
                    elif char == "}":
                        if stack and stack[-1] == "{":
                            stack.pop()
                            cursor += 1
                        elif stack[-1] == "@put:{":
                            stack.pop()
                            tokenList.append(tmpStr[:-1])
                            tokenList.append("}")
                            cursor += 1
                            tmpStr = ""
                            break
                    else:
                        cursor += 1
            elif (result := ck(cursor, tmpStr[:-1], "@css:"))[2]:
                cursor, tmpStr, __ = result
            elif (result := ck(cursor, tmpStr[:-1], "@json:", "@json:"))[2]:
                cursor, tmpStr, __ = result
            elif (
                result := ck(
                    cursor,
                    tmpStr[:-1],
                    "@@",
                )
            )[2]:
                cursor, tmpStr, __ = result
            elif (result := ck(cursor, tmpStr[:-1], "@js:"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "#":
                        if (result := ck(cursor, tmpStr[:-1], "###"))[2]:
                            cursor, tmpStr, __ = result
                            break
                        elif (result := ck(cursor, tmpStr[:-1], "##"))[2]:
                            cursor, tmpStr, __ = result
                        else:
                            cursor += 1
                    else:
                        cursor += 1
                # tmpStr = text[cursor:]
                # break
            elif text[cursor - 1] == "[":
                cursor += 1
            elif stack and stack[-1].lower() == "@json:":
                cursor += 1
            else:
                tokenList.append(tmpStr[:-1])
                tokenList.append("@")
                cursor += 1
                tmpStr = ""
        elif char == "{":
            if (result := ck(cursor, tmpStr[:-1], "{{", "{{"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "{":
                        stack.append("{")
                        cursor += 1
                    elif char == "}":
                        if stack and stack[-1] == "{":
                            stack.pop()
                            cursor += 1
                        elif (result := ck(cursor, tmpStr[:-1], "}}", "{{", -1, "{{"))[
                            2
                        ]:
                            cursor, tmpStr, __ = result
                            break
                        else:
                            cursor += 1
                    else:
                        cursor += 1
            # elif (result := ck(cursor, tmpStr[:-1], '{', '{'))[2]:
            #     cursor, tmpStr, __ = result
            elif len(text) - 1 > cursor + 3 and text[cursor : cursor + 3] == "{$.":
                stack.append("{")
                tokenList.append(tmpStr[:-1])
                tokenList.append("{")
                cursor += 1
                tmpStr = ""

            else:
                # stack.append('{')
                cursor += 1
        elif char == "}":
            if (result := ck(cursor, tmpStr[:-1], "}", "", -1, "{"))[2]:
                cursor, tmpStr, __ = result
            # if stack and stack[-1] == '{':
            #     stack.pop()
            #     cursor += 1
            else:
                cursor += 1
        elif char == "|":
            if stack and stack[-1] == "{{":
                cursor += 1
            if (result := ck(cursor, tmpStr[:-1], "||"))[2]:
                cursor, tmpStr, __ = result
            else:
                cursor += 1
        elif char == "&":
            if len(text) - 1 < cursor + 1:
                break
            elif text[cursor + 1] == "&" and not (stack and stack[0] != "@json:"):
                tokenList.append(tmpStr[:-1])
                tokenList.append("&&")
                cursor += 2
                tmpStr = ""
            else:
                cursor += 1
        elif char == "%":
            if len(text) - 1 < cursor + 1:
                break
            elif text[cursor + 1] == "%" and not (stack and stack[0] != "@json:"):
                tokenList.append(tmpStr[:-1])
                tokenList.append(r"%%")
                cursor += 2
                tmpStr = ""
            else:
                cursor += 1
        elif char == "<":
            if (result := ck(cursor, tmpStr[:-1], "<js>", "<js>"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "<":
                        if (
                            result := ck(
                                cursor,
                                tmpStr[:-1],
                                "</js>",
                                stackIndex=-1,
                                stackText="<js>",
                            )
                        )[2]:
                            cursor, tmpStr, __ = result
                            break
                        else:
                            cursor += 1
                    else:
                        cursor += 1
            # elif (result := ck(cursor, tmpStr[:-1], '</js>', stackIndex=-1, stackText='<js>'))[2]:
            #     cursor, tmpStr, __ = result
            else:
                cursor += 1
        elif char == "\\":
            tmpStr += text[cursor + 1]
            cursor += 2
        elif (char in {"+", "-", ":"}) and cursor == 0:
            tokenList.append(char)
            cursor += 1
            tmpStr = ""
        elif char == ":" and cursor == 1:
            tokenList.append(char)
            cursor += 1
            tmpStr = ""
        elif char == "#":
            if (result := ck(cursor, tmpStr[:-1], "####"))[2]:
                cursor, tmpStr, __ = result
            # elif (result := ck(cursor, tmpStr[:-1], '###'))[2]:
            #     cursor, tmpStr, __ = result
            elif (result := ck(cursor, tmpStr[:-1], "##"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "#":
                        if (result := ck(cursor, tmpStr[:-1], "###"))[2]:
                            cursor, tmpStr, __ = result
                            break
                        elif (result := ck(cursor, tmpStr[:-1], "##"))[2]:
                            cursor, tmpStr, __ = result

                        else:
                            cursor += 1
                    elif char == "@":
                        if (result := ck(cursor, tmpStr[:-1], "@js:"))[2]:
                            cursor, tmpStr, __ = result
                            tmpStr = text[cursor:]
                            cursor = len(text)
                            break
                        else:
                            cursor += 1
                    else:
                        cursor += 1
            else:
                cursor += 1
        elif char == "$":
            if len(text) - 1 < cursor + 1:
                break
            if text[cursor + 1].isnumeric():
                tokenList.append(tmpStr[:-1])
                tokenList.append("$" + text[cursor + 1])
                cursor += 2
                tmpStr = ""
            else:
                cursor += 1
        else:
            cursor += 1

    tokenList.append(tmpStr)

    # return list(filter(lambda x: x.strip(), tokenList)) # 不可以这样写
    return list(filter(None, tokenList))


def tokenizerUrl(text: str) -> List[str]:

    tokenList:List[str] = []
    stack:List[str] = []
    cursor = 0
    length = len(text)
    tmpStr = ""
    char = ""
    ck = Check(text, stack, tokenList).ck
    while cursor < length:
        char = text[cursor]
        tmpStr += char
        if char == "@":
            if (result := ck(cursor, tmpStr[:-1], "@js:"))[2]:
                cursor, tmpStr, __ = result
                tmpStr = text[cursor:]
                break
            else:
                cursor += 1
        elif char == "{":
            if (result := ck(cursor, tmpStr[:-1], "{{", "{{"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "{":
                        stack.append("{")
                        cursor += 1
                    elif char == "}":
                        if stack and stack[-1] == "{":
                            stack.pop()
                            cursor += 1
                        elif (result := ck(cursor, tmpStr[:-1], "}}", "{{", -1, "{{"))[
                            2
                        ]:
                            cursor, tmpStr, __ = result
                            break
                        else:
                            cursor += 1
                    else:
                        cursor += 1

            else:
                cursor += 1

        elif char == "<":
            if (result := ck(cursor, tmpStr[:-1], "<js>", "<js>"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "<":
                        if (
                            result := ck(
                                cursor,
                                tmpStr[:-1],
                                "</js>",
                                stackIndex=-1,
                                stackText="<js>",
                            )
                        )[2]:
                            cursor, tmpStr, __ = result
                            break
                        else:
                            cursor += 1
                    else:
                        cursor += 1
            elif (result := ck(cursor, tmpStr[:-1], "<", "<"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == ">":
                        if (
                            result := ck(
                                cursor, tmpStr[:-1], ">", stackIndex=-1, stackText="<"
                            )
                        )[2]:
                            cursor, tmpStr, __ = result
                            break
                        else:
                            cursor += 1
                    else:
                        cursor += 1
            else:
                cursor += 1
        elif char == "\\":
            tmpStr += text[cursor + 1]
            cursor += 2

        else:
            cursor += 1

    tokenList.append(tmpStr)
    return list(filter(None, tokenList))


def tokenizerInner(text: str) -> List[str]:
    tokenList:List[str] = []
    stack:List[str] = []
    cursor = 0
    length = len(text)
    tmpStr = ""
    char = ""
    ck = Check(text, stack, tokenList).ck
    while cursor < length:
        char = text[cursor]
        tmpStr += char

        if char == "{":
            if (result := ck(cursor, tmpStr[:-1], "{{", "{{"))[2]:
                cursor, tmpStr, __ = result
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "{":
                        stack.append("{")
                        cursor += 1
                    elif char == "}":
                        if stack and stack[-1] == "{":
                            stack.pop()
                            cursor += 1
                        elif (result := ck(cursor, tmpStr[:-1], "}}", "{{", -1, "{{"))[
                            2
                        ]:
                            cursor, tmpStr, __ = result
                            break
                        else:
                            cursor += 1
                    else:
                        cursor += 1
            else:
                stack.append("{")
                cursor += 1

        else:
            cursor += 1

    tokenList.append(tmpStr)
    return list(filter(None, tokenList))


def splitPage(text):
    tokenList = []
    stack = []
    cursor = 0
    length = len(text)
    tmpStr = ""
    char = ""
    ck = Check(text, stack, tokenList).ck
    while cursor < length:
        char = text[cursor]
        tmpStr += char

        if char == "{":
            if len(text) - 1 < cursor + 1:
                break
            if text[cursor : cursor + 2] == "{{":
                cursor += 1
                while cursor < length:
                    char = text[cursor]
                    tmpStr += char
                    if char == "{":
                        stack.append("{")
                        cursor += 1
                    elif char == "}":
                        if stack and stack[-1] == "{":
                            stack.pop()
                            cursor += 1
                        elif (not len(text) - 1 < cursor + 1) and text[
                            cursor : cursor + 2
                        ] == "}}":
                            cursor += 1
                            break
                        else:
                            cursor += 1
                    else:
                        cursor += 1
            else:
                cursor += 1
        elif char == ",":
            if (result := ck(cursor, tmpStr[:-1], ","))[2]:
                cursor, tmpStr, __ = result
        else:
            cursor += 1

    tokenList.append(tmpStr)
    return list(filter(lambda x: x != ",", tokenList))


class Check:
    def __init__(self, text, stack, tokenList):
        self.text = text
        self.stack = stack
        self.tokenList = tokenList
        self.length = len(self.text)

    def ck(
        self, cursor, tmpStr, tokenText="", pushStack="", stackIndex=None, stackText=""
    ):
        if self.length < cursor + len(tokenText):
            return cursor, tmpStr, False

        if (
            tokenText
            and self.text[cursor : cursor + len(tokenText)].lower() == tokenText
        ):
            if stackIndex:
                if self.stack and self.stack[stackIndex] == stackText:
                    self.stack.pop()
                else:
                    return cursor, tmpStr, False

            elif pushStack:
                self.stack.append(pushStack)

            self.tokenList.append(tmpStr)
            self.tokenList.append(tokenText)
            cursor += len(tokenText)
            tmpStr = ""
            return cursor, tmpStr, True
        elif not tokenText:
            if self.stack and self.stack[stackIndex] == stackText:
                self.stack.pop()
                return cursor, tmpStr, True
            else:
                return cursor, tmpStr, False
        else:
            return cursor, tmpStr, False


# print(tokenizer(r".zp@a@href##(\\d+)##$1###@js:var xid=Math.floor(result/1000);'http://www.cfwx.org/files/article/image/'+xid+'/'+result+'/'+result+'s.jpg';"))
# print(tokenizer(
#     '''[property=\"og:novel:category\"]@content&&[property=\"og:novel:status\"]@content&&[property=\"og:novel:update_time\"]@content##小说|\\s.*'''))
# print(tokenizer('''@JSon:$..body&&$..cpContent@js:result.replace(/请安装.*/g,\"\")'''))
# print(tokenizer('''{{$.chapterName}}·{{$.chapterUpdateTime}}##T.*'''))
# print(tokenizer('''//div[@id=\"list\"]/dl/dt[2]/following-sibling::dd'''))
# print(tokenizer('''id.info@tag.a.-1@text&&id.info@tag.p.-2@text##最后更新.|..\\:.*'''))
# print(tokenizer('''//*[text()=\"总字数\"]//text()##总字数##字'''))
# print(tokenizer('@get:{}'))
# print(tokenizer('id.details@text##.*最新：|\\|\\||更新时间.|..\\:.*'))
# print(tokenizer('class.author@text##作者：||tag.a.2@text'))
# print(tokenizer('https://www.zhaishuyuan.org/search/?searchkey={{key}}'))
# print(tokenizer('https://www.longtanshuwang.com/s666.php?ie=gbk&q={{key}}'))
# print(tokenizer('class.book-img-text@tag.li||class.book-list-wrap@class.book-list@tag.li'))
# print(tokenizerInner("""sign_key='d3dGiJc651gSQ8w1'

# params={'id':{{$.id}},'imei_ip':'2937357107','teeny_mode':0}

# var urlEncode = function (param, key, encode) {
#   if(param==null) return '';
#   var paramStr = '';
#   var t = typeof (param);
#   if (t == 'string' || t == 'number' || t == 'boolean') {
#     paramStr += '&' + key + '=' + ((encode==null||encode) ? encodeURIComponent(param) : param);
#   } else {
#     for (var i in param) {
#       var k = key == null ? i : key + (param instanceof Array ? '[' + i + ']' : '.' + i);
#       paramStr += urlEncode(param[i], k, encode);
#     }
#   }
#   return paramStr;
# };
# paramSign=String(java.md5Encode(Object.keys(params).sort().reduce((pre,n)=>pre+n+'='+params[n],'')+sign_key))
# params['sign']=paramSign
# "/api/v4/book/detail?"+urlEncode(params)+","+java.get("headers")"""))
# print(tokenizer('@css:.list>dl a<js>result</js>a:nth-child(3N)%%a:nth-child(3N-1)%%a:nth-child(3N-2)'))
# print(tokenizer('####'))
# print(tokenizer(
#     'tag.a.0@href##.+\\D((\\d+)\\d{3})\\D##http://www.ujxs.com/files/article/image/$2/$1/$1s.jpg###'))
# print(tokenizerUrl('/sort/xuanhuan/<,{{page}}.html>'))
# print(splitPage('1,abc{{,{},}}}def'))
# print(tokenizerUrl('/search/{{key}}<,/{{page}}.html>'))
