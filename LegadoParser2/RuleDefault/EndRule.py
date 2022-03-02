from lxml.etree import XPath


class EndRuleXpath:
    textNodes = XPath('./text()')
    ownText = textNodes
    text = XPath('.//text()')
    html = XPath('.//script|.//style')
    src = XPath('./@src')
    href = XPath('./@href')

    @classmethod
    def get(cls, endRule):
        try:
            return getattr(cls, endRule)
        except AttributeError:
            return XPath(f'./@{endRule}')
