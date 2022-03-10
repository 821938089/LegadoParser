import re
from lxml.etree import _Element, tostring


def regexProcessor(content, rule, **kwargs):
    regexType = rule['preProcess']['regexType']
    reObj = rule['preProcess']['body']['reObj']
    replacement = rule['preProcess']['body']['replacement']
    regex = rule['preProcess']['body']['regex']
    replaceFirst = rule['preProcess']['body']['replaceFirst']

    if regexType == 'allInOne':
        return reObj.findall(content)
    elif regexType == 'onlyOne':
        if isinstance(content, _Element):
            if content.tag == 'html':
                content = kwargs.get('rawContent', '')
            else:
                content = tostring(content, encoding='utf-8').decode('utf-8')
        elif isinstance(content, list):
            content = '\n'.join(content)
        match = reObj.search(content)
        return [re.sub(r'(?<!\\)\$\d', lambda x:match[int(x[0][1])] if match else "", replacement)]
    elif regexType == 'replace':
        if not isinstance(content, list):
            content = [content]

        content = list(filter(lambda x: isinstance(x, str), content))
        if replaceFirst:
            for i in range(len(content)):
                content[i] = reObj.sub(replacement, content[i], 1)
        else:
            for i in range(len(content)):
                content[i] = reObj.sub(replacement, content[i])
        # if regex == '$':
        #     for i in range(len(content)):
        #         content[i] += replacement
        # else:
        #     captureGroupRegex = re.compile(r'(?<!\\)\$\d')
        #     for i in range(len(content)):
        #         for m in reObj.finditer(content[i]):
        #             old = m[0]
        #             if replacement:
        #                 new = captureGroupRegex.sub(lambda x: m[int(x[0][1])], replacement)
        #             else:
        #                 new = ''
        #             content[i] = content[i].replace(old, new, 1)
        #             if replaceFirst:
        #                 break
        return content
