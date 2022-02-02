

class RuleNotFoundError(Exception):
    '''找不到不可省略的规则'''
    pass


class RuleNotSupportError(Exception):
    '''规则不支持'''
    pass


class RuleSyntaxError(Exception):
    '''规则语法错误'''
    pass


class RuleCompileError(Exception):
    '''规则预编译失败'''
    pass
