def validateFlag(flag):
    """
    将 isPay isVip isVolume 转换为布尔值
    当 flag 为"None" "False" "0" "" "null"时返回False
    其余情况返回True
    """
    falseSet = {'none', 'false', '0', '', 'null'}
    if flag.lower() in falseSet:
        return False
    else:
        return True
