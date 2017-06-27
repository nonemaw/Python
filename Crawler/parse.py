
import re
import datetime
import logging
from config import get_url_legal

class Parser:
    def __init__(self, max_deep=-1):
        """
        :param max_deep: define depth of crawler, -1 means infinite
        """
        self._max_deep = max_deep

    def parse_working(self, priority:int, url:str, keys:object, deep:int,
                      content:object) -> (int, list, list):
        """
        working function, must "try, except" and don't change the parameters and return
        :return (parse_result, url_list, save_list): parse_result can be
            -1 (parse failed),
             1 (parse success)

        url_list[]: (url, keys, priority)
        """

        # FIXME
        logging.warning("%s Parser start: priority=%s, keys=%s, deep=%s, url=%s", self.__class__.__name__, priority, keys, deep, url)

        try:
            parse_result, url_list, finger_print = self.html_parse(priority, url, keys, deep, content)
        except Exception as E:

            # FIXME
            logging.warning("%s Parser ERROR: %s", self.__class__.__name__, E)

            parse_result, url_list, finger_print = -1, [], []

        # FIXME
        logging.warning("%s Parser end: parse_result=%s, len(url_list)=%s, len(finger_print)=%s, url=%s", self.__class__.__name__, parse_result, len(url_list), len(finger_print), url)

        return parse_result, url_list, finger_print

    def html_parse(self, priority:int, url:str, keys:object, deep:int, content:object) -> (int, list, list):
        """
        parse the content of a url, you can rewrite this function, parameters and return refer to self.parse_working()
        A <a href> attribute specifies the link's destination:
            <a href="https://www.sample.com">Visitor</a>

        content = (response.status_code, response.url, response.text)
        """
        *_, html_text = content
        url_list = []

        if(self._max_deep < 0) or (deep < self._max_deep):
            # re.findall() returns a list of matched elements
            href_list = re.findall(r"<a[\w\W]+?href=\"(?P<url>[\w\W]{5,}?)\"[\w\W]*?>[\w\W]+?</a>",
                                   html_text, flags=re.IGNORECASE)
            url_list = [(_url, keys, priority+1)
                        for _url in [get_url_legal(href_tag, url) for href_tag in href_list]]

        # re.search() returns a MatchObject with matched locations in a string, using .group() to get data
        title = re.search(r"<title>(?P<title>[\w\W]+?)</title>",
                          html_text,
                          flags=re.IGNORECASE)
        finger_print = [(title.group("title").strip(), datetime.datetime.now()), ] if title else []
        return 1, url_list, finger_print
