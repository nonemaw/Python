
import queue
import threading
import copy
import logging
from thread_base import FLAGS, BasePool, FetchThread, ParseThread, SaveThread


class ThreadPool(BasePool):
    """
    fetcher/parser/saver are instance of class Fetcher, Parser and Saver
    """

    def __init__(self, fetcher, parser, saver, url_filter=None):
        """
        :param fetcher: instance of class Fetcher
        :param parser: instance of class Parser
        :param saver: instance of class Saver
        :param url_filter: whether conduct repetitive check
        """
        BasePool.__init__(self, fetcher, parser, saver, url_filter=url_filter)
        self._fetch_queue = queue.PriorityQueue()
        self._parse_queue = queue.PriorityQueue()
        self._save_queue = queue.Queue()
        self._lock = threading.Lock()

    def run(self, url, keys=None, priority=0, deep=0, fetcher_num=10, repeat=0):
        """
        :url: page address
        :keys: keywords for parse
        :priority: for PriorityQueue only
        :deep: working depth
        :fetcher_num: number of FetcherThread
        """

        # FIXME
        logging.warning("%s ThreadPool start: fetcher_num=%s", self.__class__.__name__, fetcher_num)

        self.add_task(FLAGS.URL_FETCH, (priority, url, keys, deep, repeat))

        if isinstance(self._fetcher, (list, tuple)):
            fetch_thread_list = [
                FetchThread("fetcher-{}".format(str(i + 1)), fetcher, self)
                for (i, fetcher) in enumerate(self._fetcher)]
        else:
            fetch_thread_list = [FetchThread("fetcher-{}".format(str(i + 1)),
                                 copy.deepcopy(self._fetcher), self)
                                 for i in range(fetcher_num)]
        parse_save_thread_list = [ParseThread("parser", self._parser, self),
                                  SaveThread("saver", self._saver, self)]

        for fetch_thread in fetch_thread_list:
            fetch_thread.daemon = True  # running background
            # run() and start_fetch() of class FetchThread() are running
            fetch_thread.start()

        for parse_save_thread in parse_save_thread_list:
            parse_save_thread.daemon = True
            # run() and start_parse() of class ParseThread() are running
            parse_save_thread.start()

        # Handle unfinished FetchThread
        for fetch_thread in fetch_thread_list:
            if fetch_thread.is_alive():
                fetch_thread.join()

        while self._number_dict[FLAGS.URL_NOT_FETCH] > 0:
            self.get_task(FLAGS.URL_FETCH)
            self.finish_task(FLAGS.URL_FETCH)

        # Handle unfinished ParseThread
        for thread in parse_save_thread_list:
            if thread.is_alive():
                thread.join()

        # FIXME
        logging.warning("%s ThreadPool end: fetcher_num=%s", self.__class__.__name__, fetcher_num)

    def add_task(self, task_name, task_content):
        """
        Add a task to queue based on task_name

        Queue.put_nowait(item) equals to Queue.put(item, block=False, timeout=None)
        """
        if task_name == FLAGS.URL_FETCH and ((task_content[-1] > 0)
                                             or not self._url_filter):
            self._fetch_queue.put(task_content, block=False)
            self.update_dict(FLAGS.URL_NOT_FETCH, +1)
        elif task_name == FLAGS.HTML_PARSE:
            self._parse_queue.put(task_content, block=False)
            self.update_dict(FLAGS.HTML_NOT_PARSE, +1)
        elif task_name == FLAGS.ITEM_SAVE:
            self._save_queue.put(task_content, block=False)
            self.update_dict(FLAGS.ITEM_NOT_SAVE, +1)

    def get_task(self, task_name):
        """
        Get a task from queue based on task_name and return task_content, if
        the queue is empty raise queue.Empty

        queue.get(block, timeout):
        Remove and return an item from the queue. If optional args block is
        true and timeout is None (the default), block if necessary until an
        item is available. If timeout is a positive number, it blocks at most
        timeout seconds and raises the Empty exception if no item was available
        within that time. Otherwise (block is false), return an item if one is
        immediately available, else raise the Empty exception (timeout is
        ignored in that case).
        """
        task_content = None
        if task_name == FLAGS.URL_FETCH:
            task_content = self._fetch_queue.get(block=True, timeout=5)
            self.update_dict(FLAGS.URL_NOT_FETCH, -1)
        elif task_name == FLAGS.HTML_PARSE:
            task_content = self._parse_queue.get(block=True, timeout=5)
            self.update_dict(FLAGS.HTML_NOT_PARSE, -1)
        elif task_name == FLAGS.ITEM_SAVE:
            task_content = self._save_queue.get(block=True, timeout=5)
            self.update_dict(FLAGS.ITEM_NOT_SAVE, -1)
        self.update_dict(FLAGS.TASKS_RUNNING, +1)
        return task_content

    def finish_task(self, task_name):
        """
        Finish a task based on task_name

        queue.task_done()
        Indicate that a formerly enqueued task is complete. Used by queue
        consumer threads. For each get() used to fetch a task, a subsequent
        call to task_done() tells the queue that the processing on the task is
        complete.
        """
        if task_name == FLAGS.URL_FETCH:
            self._fetch_queue.task_done()
        elif task_name == FLAGS.HTML_PARSE:
            self._parse_queue.task_done()
        elif task_name == FLAGS.ITEM_SAVE:
            self._save_queue.task_done()
        self.update_dict(FLAGS.TASKS_RUNNING, -1)

    def update_dict(self, key, value):
        self._lock.acquire()
        self._number_dict[key] += value
        self._lock.release()
