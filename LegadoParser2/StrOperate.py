def getMiddleStr(content,startStr,endStr):
    startIndex = content.find(startStr)
    if startIndex>=0:
        startIndex += len(startStr)
    endIndex = content.find(endStr, startIndex)
    return content[startIndex:endIndex]

def getLeftStr(content,finfstr):
    startIndex = content.find(finfstr)
    if startIndex>=0:
        return content[:startIndex]
    else:
        return ""

def getRightStr(content,finfstr):
    startIndex = content.find(finfstr)
    if startIndex>=0:
        startIndex += len(finfstr)
        return content[startIndex:]
    else:
        return ""