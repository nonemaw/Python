
import random
import time
import requests
from .config import make_random_useragent

class Fetcher():
    def __init__(self, max_repeat=3, sleep_time=0):
        self._max_repeat = max_repeat
        self._sleep_time = sleep_time

    def fetch_working(self, url:str, keys:object, repeat:int) -> (int, object):
        """
        working function, must "try, expect" and don't change the parameters
        and return
        :return (fetch_result, content): fetch_result can be
            -2(fetch failed, need stop),
            -1(fetch failed), 0(need repeat),
             1(fetch success)
        :return (fetch_result, content): content can be anything
        """
        time.sleep(random.randint(0, self._sleep_time))
        try:
            fetch_result, content = self.url_fetch(url, keys, repeat)
        except Exception as excep:
            if repeat >= self._max_repeat:
                fetch_result, content = -1, None
            else:
                fetch_result, content = 0, None
        return fetch_result, content

    def url_fetch(self, url:str, keys:object, repeat:int) -> (int, object):
        response = requests.get(url,
                                headers={"User-Agent":make_random_useragent(),
                                         "Accept-Encoding":"gzip"},
                                timeout=(3.05, 10))
        content = (response.status_code, response.url, response.text)
        return 1, content



