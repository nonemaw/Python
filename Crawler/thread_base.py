
import queue
import threading
import enum

class TPEnum(enum.Enum):
    """
    status of web_spider
    """
    TASKS_RUNNING = "tasks_running"     # flag of tasks_running

    URL_FETCH = "url_fetch"             # flag of url_fetched
    HTML_PARSE = "html_parse"           # flag of html_parsed
    ITEM_SAVE = "item_save"             # flag of item_saved

    URL_NOT_FETCH = "url_not_fetch"     # flag of url_not_fetch
    HTML_NOT_PARSE = "html_not_parse"   # flag of html_not_parse
    ITEM_NOT_SAVE = "item_not_save"     # flag of item_not_save


class BaseThread(threading.Thread):
    def __init__(self, name, worker, pool):
        threading.Thread.__init__(self, name=name)
        self._worker = worker     # Fetcher/Parser
        self._thread_pool = pool  # ThreadPool

    def run(self):
        while True:
            try:  # if working() returns False, which means working() done
                if not self.working(): break
            except queue.Empty:
                if self._thread_pool.all_task_done(): break
            except Exception as excep:
                break


class BasePool():
    def __init__(self, fetcher, parser, saver, url_filter=None):
        self._url_filter = url_filter  # instance of Filter, None by default
        self._inst_fetcher = fetcher   # instance of Fetcher
        self._inst_parser = parser     # instance of Parser
        self._inst_saver = saver       # instance of Saver
        self._number_dict = {
            TPEnum.TASKS_RUNNING: 0,   # the count of tasks which are running

            TPEnum.URL_FETCH: 0,       # the count of urls which have been fetched successfully
            TPEnum.HTML_PARSE: 0,      # the count of urls which have been parsed successfully
            TPEnum.ITEM_SAVE: 0,       # the count of urls which have been saved successfully

            TPEnum.URL_NOT_FETCH: 0,   # the count of urls which haven't been fetched
            TPEnum.HTML_NOT_PARSE: 0,  # the count of urls which haven't been parsed
            TPEnum.ITEM_NOT_SAVE: 0,   # the count of urls which haven't been saved
        }

    def run(self, fetcher_num=10, is_over=True):
        raise NotImplementedError


def start_fetch(self):
    priority, url, keys, deep, repeat = self._thread_pool.get_task(
                                                            TPEnum.URL_FETCH)
    fetch_result, content = self._worker.fetch_working(url, keys, repeat)

    if fetch_result == 1:
        self._thread_pool.update_dict(TPEnum.URL_FETCH, +1)
        self._thread_pool.add_task(TPEnum.HTML_PARSE, (priority, url, keys,
                                                       deep, content))
    elif fetch_result == 0:
        self._thread_pool.add_task(TPEnum.URL_FETCH, (priority+1, url, keys,
                                                      deep, repeat+1))

    self._thread_pool.finish_task(TPEnum.URL_FETCH)
    return False if fetch_result == -2 else True

# Class of FetchThread (from BaseThread), with method alias "working()" to
# start_fetch()
FetchThread = type("FetchThread", (BaseThread,), dict(working=start_fetch))


def start_parse(self):
    priority, url, keys, deep, content = self._thread_pool.get_task(
                                                            TPEnum.HTML_PARSE)
    parse_result, url_list, save_list = self._worker.parse_working(priority,
                                                    url, keys, deep, content)

    if parse_result > 0:
        self._thread_pool.update_dict(TPEnum.HTML_PARSE, +1)
        for _url, _keys, _priority in url_list:
            self._thread_pool.add_task(TPEnum.URL_FETCH, (_priority, _url,
                                                          _keys, deep+1, 0))
        for item in save_list:
            self._thread_pool.add_task(TPEnum.ITEM_SAVE, (url, keys, item))

    self._thread_pool.finish_task(TPEnum.HTML_PARSE)
    return True

# Class of ParseThread (from BaseThread), with method alias "working()" to
# start_parse()
ParseThread = type("ParseThread", (BaseThread,), dict(working=start_parse))


def start_save(self):
    url, keys, item = self._thread_pool.get_task(TPEnum.ITEM_SAVE)
    save_result = self._worker.save_working(url, keys, item)

    if save_result:
        self._thread_pool.update_dict(TPEnum.ITEM_SAVE, +1)

    self._thread_pool.finish_task(TPEnum.ITEM_SAVE)
    return True

# Class of SaveThread (from BaseThread), with method alias "working()" to
# start_save()
SaveThread = type("SaveThread", (BaseThread,), dict(working=start_save))

