from LegadoParser2.Tokenize2 import tokenizerUrl
from LegadoParser2.RulePacket import preProcessRule, packet
from functools import lru_cache


@lru_cache
def getUrlRuleObj(rule):
    return preProcessRule(packet(tokenizerUrl(rule)))
