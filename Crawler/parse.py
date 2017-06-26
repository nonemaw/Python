
import re
import datetime
from .config import get_url_legal

class Parser():
    def __init__(self, max_deep=0):
        self._max_deep = max_deep

    def parse_working(self, priority:int, url:str, keys:object, deep:int,
                      content:object) -> (int, list, list):
        """
        working function, must "try, except" and don't change the parameters and return
        :return (parse_result, url_list, save_list): parse_result can be
            -1(parse failed),
             1(parse success)
        :return (parse_result, url_list, save_list):
            url_list is [(url, keys, priority), ...],
            save_list is [item(a list or tuple), ...]
        """
        try:
            parse_result, url_list, save_list = self.html_parse(priority, url,
                                                           keys, deep, content)
        except Exception as excep:
            parse_result, url_list, save_list = -1, [], []
        return parse_result, url_list, save_list

    def html_parse(self, priority:int, url:str, keys:object, deep:int,
                   content:object) -> (int, list, list):
        """
        parse the content of a url, you can rewrite this function, parameters and return refer to self.parse_working()
        A <a href> attribute specifies the link's destination:
            <a href="https://www.sample.com">Visitor</a>

        content = (response.status_code, response.url, response.text)
        """
        *_, html_text = content
        url_list = []

        if(self._max_deep < 0) or (deep < self._max_deep):
            href_list = re.findall(r"<a[\w\W]+?href=\"(?P<url>[\w\W]{5,}?)\"[\w\W]*?>[\w\W]+?</a>",
                                   html_text, flags=re.IGNORECASE)
            url_list = [(_url, keys, priority+1)
                        for _url in
                        [get_url_legal(href_tag, url) for href_tag in href_list]]

        title = re.search(r"<title>(?P<title>[\w\W]+?)</title>",
                          html_text,
                          flags=re.IGNORECASE)
        save_list = [(title.group("title").strip(), datetime.datetime.now()), ]\
                    if title else []
        return 1, url_list, save_list
