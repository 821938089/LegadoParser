def validateFlag(flag):
    """
    将 isPay isVip isVolume 转换为布尔值
    当 flag 为"None" "False" "0" ""时返回False
    其余情况返回True
    """
    falseSet = {'None', 'False', '0', ''}
    if flag in falseSet:
        return False
    else:
        return True
