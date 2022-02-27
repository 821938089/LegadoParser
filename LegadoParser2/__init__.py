__all__ = ['Search', 'BookInfo', 'ChapterList', 'Chapter', 'RuleEval', 'RulePacket']

__version__ = '1.0.0'

from LegadoParser2.config import DEBUG_MODE

if not DEBUG_MODE:
    from LegadoParser2.Search import search
    from LegadoParser2.BookInfo import getBookInfo
    from LegadoParser2.ChapterList import getChapterList
    from LegadoParser2.Chapter import getChapterContent
    from LegadoParser2.RuleEval import getElements, getString, getStrings
    from LegadoParser2.RulePacket import getRuleObj
