
import random
import time
import requests
import logging
from config import make_random_useragent


class Fetcher:
    def __init__(self, max_repeat=3, sleep_time=0):
        """
        :param max_repeat: define counter of re-try when failure happens
        :param sleep_time: define a random sleep_time
        """
        self._max_repeat = max_repeat
        self._sleep_time = sleep_time

    def fetch_working(self, url: str, keys: object, repeat: int) -> (int, object):
        """
        :return (fetch_result, content): fetch_result can be
            -1 (fetch failed and reach max_repeat),
             0 (need repeat),
             1 (fetch success)
        """

        # FIXME
        logging.warning("%s Fetcher start: keys=%s, repeat=%s, url=%s", self.__class__.__name__, keys, repeat, url)

        time.sleep(random.randint(0, self._sleep_time))
        try:
            fetch_result, content = self.url_fetch(url)
        except Exception as excep:

            # FIXME
            logging.warning("%s Fetcher ERROR: %s", self.__class__.__name__, excep)

            if repeat >= self._max_repeat:
                fetch_result, content = -1, None
            else:
                fetch_result, content = 0, None

        # FIXME
        logging.warning("%s Fetcher end: fetch_result=%s, url=%s", self.__class__.__name__, fetch_result, url)

        return fetch_result, content

    def url_fetch(self, url:str) -> (int, object):
        response = requests.get(url,
                                headers={"User-Agent": make_random_useragent(),
                                         "Accept-Encoding": "gzip"},
                                timeout=(3.05, 10))
        return 1, (response.status_code, response.url, response.text)
