from enum import Enum

from .exceptions import RuleNotSupportError


class RuleType(Enum):
    DefaultOrEnd = 0
    Xpath = 1
    Json = 2
    Js = 3
    Regex = 4
    RuleSymbol = 5
    End = 7  # 最后的规则 text,textNodes,ownText,href,src,html,all
    Inner = 8
    Get = 9
    Put = 10
    Order = 11  # + - 符号
    UnKnown = 12  # 未知
    Format = 13  # 格式化字符串/拼接规则 包含有 $1 @get:{ } {{ }} { } 等规则
    JsonInner = 14
    JoinSymbol = 15
    Page = 16  # <,{{ }}>规则


def getRuleType(rules, index, hasEndRule=False, contentIsJson=False):
    ruleSeperatorSet = {'@', '@@', '{{', '}}', '<js>', '</js>',
                        '@js:', '@css:', '@xpath:', '@json:', '&&', '||', r'%%', '##', '###', '}', '@put:{', '@get:{', '+', '-', ':', '<', '>'}
    # ruleEndSet = {'text', 'textNodes', 'ownText', 'html', 'all'}
    ruleJoinSet = {'&&', '||', '%%', '##'}  # ‘##’不是连接符号，不想把判断结束规则条件写的太复杂了，就放一起了
    if rules[index] in ruleSeperatorSet:
        return RuleType.RuleSymbol
    elif index > 0 and rules[index - 1] in {'##', ':'}:
        return RuleType.Regex
    elif len(rules[index]) == 2 and rules[index][0] == '$' and rules[index][1].isnumeric():
        return RuleType.Regex
    elif index > 0 and rules[index - 1] in {'@css:', '@@'}:
        return RuleType.DefaultOrEnd
    elif index > 0 and rules[index - 1] in {'@js:', '<js>'}:
        return RuleType.Js
    elif index > 0 and rules[index - 1] == '@get:{':
        return RuleType.Get
    elif index > 0 and rules[index - 1] == '@put:{':
        return RuleType.Put
    elif index > 0 and rules[index - 1] == '{{':
        return RuleType.Inner
    elif index > 0 and rules[index - 1] == '{':
        return RuleType.JsonInner
    elif index > 0 and rules[index - 1] == '<':
        return RuleType.Page
    elif rules[index].startswith('/') and not ('{{' in rules or '@get:{' in rules):
        return RuleType.Xpath
    elif rules[index].startswith('$.') or rules[index].startswith('$['):
        return RuleType.Json
    elif contentIsJson:
        return RuleType.Json
    elif hasEndRule and (index == len(rules) - 1 or rules[index + 1] in ruleJoinSet):
        return RuleType.End
    else:
        return RuleType.DefaultOrEnd


# 规则分组专用函数
def getRuleTypeForGroup(rulesTokens, index):
    ruleSeperatorSet = {'@', '{{', '}}', '<js>', '</js>',
                        '@js:', '@css:', '@xpath:', '@json:', '&&', '||', r'%%', '##', '###', '}', '@put:{', '@get:{', '+', '-', ':'}
    ruleDefaultSeperatorSet = {'@', '@css:', '@@'}
    ruleJsSeperatorSet = {'<js>', '</js>', '@js:'}
    ruleJsonSeperatorSet = {'@json:'}
    ruleRegexSeperatorSet = {'##', '###', ':', '####'}
    ruleOrderSeperatorSet = {'+', '-'}
    ruleInnerSeperatorSet = {'{{', '}}'}
    ruleJsonInnerSeperatorSet = {'{'}  # 右花括号(})可能是put规则的，不能放这里比较
    ruleFormatSeperatorSet = {'{{', '}}', '{', '}', '@get:{', '<', '>'}
    rulePageSeperatorSet = {'<', '>'}
    # ruleEndSet = {'text', 'textNodes', 'ownText', 'html', 'all'}
    ruleJoinSet = {'&&', '||', '%%'}
    length = len(rulesTokens)
    # ------------自身预测-------------
    if rulesTokens[index] in ruleDefaultSeperatorSet:
        return RuleType.DefaultOrEnd
    elif rulesTokens[index] in ruleJsSeperatorSet:
        return RuleType.Js
    elif rulesTokens[index] in ruleJsonSeperatorSet:
        return RuleType.Json
    elif rulesTokens[index] in ruleRegexSeperatorSet:
        return RuleType.Regex
    elif rulesTokens[index] in ruleOrderSeperatorSet and index == 0:
        return RuleType.Order
    elif rulesTokens[index] in ruleInnerSeperatorSet:
        return RuleType.Format
    elif rulesTokens[index] in ruleJsonInnerSeperatorSet:
        return RuleType.Format
    elif rulesTokens[index] in rulePageSeperatorSet:
        return RuleType.Format
    elif rulesTokens[index] in ruleJoinSet:
        return RuleType.JoinSymbol
    elif rulesTokens[index] == '@get:{':
        return RuleType.Format
    elif rulesTokens[index] == '@put:{':
        return RuleType.Put
    # ------------自身预测-------------
    # ------------前向预测-------------
    elif index > 0 and rulesTokens[index - 1] in ruleDefaultSeperatorSet:
        return RuleType.DefaultOrEnd
    elif index > 0 and rulesTokens[index - 1] in {'##', '####', ':'}:
        return RuleType.Regex
    elif index > 0 and rulesTokens[index - 1] in {'<js>', '@js:'}:
        return RuleType.Js
    elif index > 0 and rulesTokens[index - 1] == '@put:{':
        return RuleType.Put
    elif index > 0 and rulesTokens[index - 1] in ruleFormatSeperatorSet:
        return RuleType.Format
    elif index > 0 and len(rulesTokens[index - 1]) == 2 and rulesTokens[index - 1][0] == '$' and rulesTokens[index - 1][1].isnumeric():
        return RuleType.Format
    elif rulesTokens[index] == '}' and rulesTokens[index - 2] in {'@get:{', '{'}:
        return RuleType.Format
    elif rulesTokens[index] == '}' and rulesTokens[index - 2] == '@put:{':
        return RuleType.Put
    # ------------前向预测-------------
    # $1规则可能是Regex和Format，需要优先判断是否是Regex，故需要先前向预测再自身预测
    elif len(rulesTokens[index]) == 2 and rulesTokens[index][0] == '$' and rulesTokens[index][1].isnumeric():
        return RuleType.Format
    # ------------后向预测-------------
    elif index + 1 < length and rulesTokens[index + 1] in {'{{', '{', '@get:{'}:
        return RuleType.Format
    elif index + 1 < length and len(rulesTokens[index + 1]) == 2 and rulesTokens[index + 1][0] == '$' and rulesTokens[index + 1][1].isnumeric():
        return RuleType.Format
    # ------------后向预测-------------
    elif rulesTokens[index].startswith('$.') or rulesTokens[index].startswith('$['):
        return RuleType.Json
    elif rulesTokens[index].startswith('/'):
        return RuleType.Xpath
    elif index == 0 and length == 1:
        return RuleType.DefaultOrEnd
    else:
        return RuleType.DefaultOrEnd
