
import queue
import threading
import enum

class TPEnum(enum.Enum):
    """
    status of web_spider
    """
    TASKS_RUNNING = "tasks_running"     # flag of tasks_running

    URL_FETCH = "url_fetch"             # flag of url_fetched
    HTM_PARSE = "htm_parse"             # flag of htm_parsed
    ITEM_SAVE = "item_save"             # flag of item_saved

    URL_NOT_FETCH = "url_not_fetch"     # flag of url_not_fetch
    HTM_NOT_PARSE = "htm_not_parse"     # flag of htm_not_parse
    ITEM_NOT_SAVE = "item_not_save"     # flag of item_not_save


class BaseThread(threading.Thread):
    def __init__(self, name, worker, pool):
        threading.Thread.__init__(self, name=name)
        self._worker = worker  # Fetcher/Parser
        self._pool = pool      # ThreadPool

    def run(self):
        while True:
            try:
                if not self.working(): break  # if working() returns False, which means working() done
            except queue.Empty:
                if self._pool.all_task_done(): break
            except Exception as excep:
                break

class BasePool():
    def __init__(self, fetcher, parser, saver, url_filter=None):
        self._inst_fetcher = fetcher  # instance of Fetcher
        self._inst_parser = parser    # instance of Parser
        self._inst_saver = saver      # instance of Saver
        self._number_dict = {
            TPEnum.TASKS_RUNNING: 0,  # the count of tasks which are running

            TPEnum.URL_FETCH: 0,      # the count of urls which have been fetched successfully
            TPEnum.HTM_PARSE: 0,      # the count of urls which have been parsed successfully
            TPEnum.ITEM_SAVE: 0,      # the count of urls which have been saved successfully

            TPEnum.URL_NOT_FETCH: 0,  # the count of urls which haven't been fetched
            TPEnum.HTM_NOT_PARSE: 0,  # the count of urls which haven't been parsed
            TPEnum.ITEM_NOT_SAVE: 0,  # the count of urls which haven't been saved
        }

    def run(self, fetcher_num=10, is_over=True):
        raise NotImplementedError



def work_fetch(self):
    priority, url, keys, deep, repeat = self._pool.get_task(TPEnum.URL_FETCH)
    fetch_result, content = self._worker.fetch_working(url, keys, repeat)

    if fetch_result == 1:
        self._pool.update_dict(TPEnum.URL_FETCH, +1)
        self._pool.add_task(TPEnum.HTM_PARSE, (priority, url, keys, deep, content))
    elif fetch_result == 0:
        self._pool.add_task(TPEnum.URL_FETCH, (priority+1, url, keys, deep, repeat+1))

    self._pool.finish_task(TPEnum.URL_FETCH)
    return False if fetch_result == -2 else True

# Class of FetchThread (from BaseThread), with method "working()" from work_fetch
FetchThread = type("FetchThread", (BaseThread,), dict(working=work_fetch))


def work_parse(self):
    priority, url, keys, deep, content = self._pool.get_task(TPEnum.HTM_PARSE)
    parse_result, url_list, save_list = self._worker.parse_working(priority, url, keys, deep, content)

    if parse_result > 0:
        self._pool.update_dict(TPEnum.HTM_PARSE, +1)
        for _url, _keys, _priority in url_list:
            self._pool.add_task(TPEnum.URL_FETCH, (_priority, _url, _keys, deep+1, 0))
        for item in save_list:
            self._pool.add_task(TPEnum.ITEM_SAVE, (url, keys, item))

    self._pool.finish_task(TPEnum.HTM_PARSE)
    return True

# Class of ParseThread (from BaseThread), with method "working()" from work_parse
ParseThread = type("ParseThread", (BaseThread,), dict(working=work_parse))


def work_save(self):
    url, keys, item = self._pool.get_task(TPEnum.ITEM_SAVE)
    save_result = self._worker.save_working(url, keys, item)

    if save_result:
        self._pool.update_dict(TPEnum.ITEM_SAVE, +1)

    self._pool.finish_task(TPEnum.ITEM_SAVE)
    return True

# Class of SaveThread (from BaseThread), with method "working()" from work_save
SaveThread = type("SaveThread", (BaseThread,), dict(working=work_save))

