from dataclasses import dataclass
import copy

@dataclass
class BookSourceEntity:
    comment: str
    group: str
    name: str
    type: int
    book_url_pattern: str
    url: str
    custom_order: int
    enabled: bool
    enabled_cookie_jar: bool
    enabled_explore: bool
    explore_url: str
    header: str
    last_update_time: int
    login_url: str
    respond_time: int

    def __init__(self, book_source: dict) -> None:
        self._book_source = copy.deepcopy(book_source)
        self.comment = book_source.get("bookSourceComment", "")
        self.group = book_source.get("bookSourceGroup", "")
        self.name = book_source.get("bookSourceName", "")
        self.type = book_source.get("bookSourceType", 0)
        self.url = book_source.get("bookSourceUrl", "")
        self.book_url_pattern = book_source.get("bookUrlPattern", "")
        self.custom_order = book_source.get("customOrder", 0)
        self.enabled = book_source.get("enabled", True)
        self.enabled_cookie_jar = book_source.get("enabledCookieJar", False)
        self.enabled_explore = book_source.get("enabledExplore", True)
        self.explore_url = book_source.get("exploreUrl", "")
        self.header = book_source.get("header", "")
        self.last_update_time = book_source.get("lastUpdateTime", 0)
        self.login_url = book_source.get("loginUrl", "")
        self.respond_time = book_source.get("respondTime", 0)
        self.rule_search = RuleSearch(book_source.get("ruleSearch", {}))
        self.rule_book_info = RuleBookInfo(book_source.get("ruleBookInfo", {}))
        self.rule_toc = RuleToc(book_source.get("ruleToc", {}))
        self.rule_content = RuleContent(book_source.get("ruleContent", {}))
    
    def copy(self):
        return copy.deepcopy(self)


@dataclass
class RuleBookInfo:
    init: str
    name: str
    author: str
    intro: str
    kind: str
    last_chapter: str
    cover_url: str
    update_time: str
    word_count: str
    can_re_name: str
    download_urls: str

    def __init__(self, book_info: dict) -> None:
        self._book_info = book_info
        self.init = book_info.get("init", "")
        self.name = book_info.get("name", "")
        self.author = book_info.get("author", "")
        self.intro = book_info.get("intro", "")
        self.kind = book_info.get("kind", "")
        self.last_chapter = book_info.get("lastChapter", "")
        self.cover_url = book_info.get("coverUrl", "")
        self.update_time = book_info.get("updateTime", "")
        self.word_count = book_info.get("wordCount", "")
        self.can_re_name = book_info.get("canReName", "")
        self.download_urls = book_info.get("downloadUrls", "")

@dataclass
class RuleContent:
    content: str
    replace_regex: str
    next_content_url: str
    web_js: str
    source_regex: str
    image_style: str
    pay_action: str

    def __init__(self, rule_content: dict) -> None:
        self._rule_content = rule_content
        self.content = rule_content.get('content', "")
        self.replace_regex = rule_content.get('sourceRegex', "")
        self.next_content_url = rule_content.get('nextContentUrl', "")
        self.web_js = rule_content.get('webJs', "")
        self.source_regex = rule_content.get('replaceRegex', "")
        self.image_style = rule_content.get('imageStyle', "")
        self.pay_action = rule_content.get('payAction', "")

@dataclass
class RuleSearch:
    book_list: str
    name: str
    author: str
    intro: str
    kind: str
    last_chapter: str
    update_time: str
    book_url: str
    cover_url: str
    word_count: str
    check_keyword: str

    def __init__(self, rule_search: dict) -> None:
        self._rule_search = rule_search
        self.book_list = rule_search.get("bookList", "")
        self.name = rule_search.get("name", "")
        self.author = rule_search.get("author", "")
        self.intro = rule_search.get("intro", "")
        self.kind = rule_search.get("kind", "")
        self.last_chapter = rule_search.get("lastChapter", "")
        self.update_time = rule_search.get("updateTime", "")
        self.book_url = rule_search.get("bookUrl", "")
        self.cover_url = rule_search.get("coverUrl", "")
        self.word_count = rule_search.get("wordCount", "")
        self.check_keyword = rule_search.get("checkKeyWord", "")

@dataclass
class RuleToc:
    list: str
    name: str
    url: str
    update_time: str
    next_url: str
    pre_update_js: str
    is_volume: str
    is_vip: str
    is_pay: str

    def __init__(self, rule_toc: dict) -> None:
        self._rule_toc = rule_toc
        self.list = rule_toc.get("chapterList", "")
        self.name = rule_toc.get("chapterName", "")
        self.url = rule_toc.get("chapterUrl", "")
        self.update_time = rule_toc.get("updateTime", "")
        self.next_url = rule_toc.get("nextTocUrl", "")
        self.pre_update_js = rule_toc.get("preUpdateJs", "")
        self.is_volume = rule_toc.get("isVolume", "")
        self.is_vip = rule_toc.get("isVip", "")
        self.is_pay = rule_toc.get("isPay", "")
