
import queue
import threading
import copy
from thread_base import TPEnum, BasePool, FetchThread, ParseThread, SaveThread

class ThreadPool(BasePool):
    """
    fetcher/parser/saver are instance of FetcherThread, ParseThread and SaveThread
    """
    def __init__(self, fetcher, parser, saver, url_filter=None):
        BasePool.__init__(self, fetcher, parser, saver, url_filter=url_filter)
        self._fetch_queue = queue.PriorityQueue()
        self._parse_queue = queue.PriorityQueue()
        self._save_queue = queue.Queue()

        self._lock = threading.Lock()

    def run(self, fetcher_num=10, over=True):
        """
        fetcher_list: keep instance of FetchThread
        """
        if isinstance(self._inst_fetcher, (list, tuple)):
            fetcher_list = [FetchThread("fetcher-{}".format(str(i)), fetcher, self)
                            for (i, fetcher) in enumerate(self._inst_fetcher)]
        else:
            fetcher_list = [FetchThread("fetcher-{}".format(str(i)), copy.deepcopy(self._inst_fetcher), self)
                            for (i, fether) in range(fetcher_num)]
        parse_saver_list = [ParseThread("parser", self._inst_parser, self), SaveThread("saver", self._inst_saver, self)]

        for thread in fetcher_list:
            thread.setDarmon(True)
            thread.start()

        for thread in parse_saver_list:
            thread.setDarmon(True)
            thread.start()

        # Handle unfinished FetcheThread
        for thread in fetcher_list:
            if thread.is_alive():
                thread.join()

        while self.get_dict(TPEnum.URL_NOT_FETCH) > 0:
            self.get_task(TPEnum.URL_FETCH)
            self.finish_task(TPEnum.URL_FETCH)

        # Handle unfinished ParseThread
        for thread in parse_saver_list:
            if thread.is_alive():
                thread.join()


    def update_dict(self, key, value):
        self._lock.acquire()
        self._number_dict[key] += value
        self._lock.release()

    def add_task(self, task_name, task_content):
        """
        Add a task to queue based on task_name
        """
        if task_name == TPEnum.URL_FETCH and ((task_content[-1] > 0) or self._url_filter.check_and_add(task_content[1])):
            self._fetch_queue.put_nowait(task_content)
            self.update_dict(TPEnum.URL_NOT_FETCH, +1)
        elif task_name == TPEnum.HTM_PARSE:
            self._parse_queue.put_nowait(task_content)
            self.update_dict(TPEnum.HTM_NOT_PARSE, +1)
        elif task_name == TPEnum.ITEM_SAVE:
            self._save_queue.put_nowait(task_content)
            self.update_dict(TPEnum.ITEM_NOT_SAVE, +1)

    def get_task(self, task_name):
        """
        Get a task from queue based on task_name and return task_content, if the queue is empty raise queue.Empty

        queue.get(block, timeout):
        Remove and return an item from the queue. If optional args block is true and timeout is None (the default),
        block if necessary until an item is available. If timeout is a positive number, it blocks at most timeout
        seconds and raises the Empty exception if no item was available within that time. Otherwise (block is false),
        return an item if one is immediately available, else raise the Empty exception (timeout is ignored in that
        case).
        """
        task_content = None
        if task_name == TPEnum.URL_FETCH:
            task_content = self._fetch_queue.get(block=True, timeout=5)
            self.update_dict(TPEnum.URL_NOT_FETCH, -1)
        elif task_name == TPEnum.HTM_PARSE:
            task_content = self._parse_queue.get(block=True, timeout=5)
            self.update_dict(TPEnum.HTM_NOT_PARSE, -1)
        elif task_name == TPEnum.ITEM_SAVE:
            task_content = self._parse_queue.get(block=True, timeout=5)
            self.update_dict(TPEnum.ITEM_NOT_SAVE, -1)
        self.update_dict(TPEnum.TASKS_RUNNING, +1)
        return task_content

    def finish_task(self, task_name):
        """
        Finish a task based on task_name

        queue.task_done()
        Indicate that a formerly enqueued task is complete. Used by queue consumer threads. For each get() used to
        fetch a task, a subsequent call to task_done() tells the queue that the processing on the task is complete.
        """
        if task_name == TPEnum.URL_FETCH:
            self._fetch_queue.task_done()
        elif task_name == TPEnum.HTM_PARSE:
            self._parse_queue.task_done()
        elif task_name == TPEnum.ITEM_SAVE:
            self._save_queue.task_done()
        self.update_dict(TPEnum.TASKS_RUNNING, -1)

