from LegadoParser2.Tokenize2 import tokenizerUrl
from LegadoParser2.RuleCompile import preProcessRule, groupTokensByType
from functools import lru_cache


@lru_cache
def getUrlRuleObj(rule):
    return preProcessRule(groupTokensByType(tokenizerUrl(rule)))
