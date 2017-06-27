
import sys
import logging

class Saver:
    def __init__(self, pipe=sys.stdout):
        """
        :param pipe: define output method
        """
        self._pipe = pipe

    def save_working(self, url:str, keys:object, finger:(list, tuple)) -> bool:
        """
        working function, must "try, except" and don't change the parameters and return
        :return save_result: True or False
        """

        # FIXME
        logging.warning("%s Saver start: keys=%s, url=%s", self.__class__.__name__, keys, url)

        try:
            save_result = self.item_saver(url, keys, finger)
        except Exception as E:

            # FIXME
            logging.warning("%s Saver ERROR: %s", self.__class__.__name__, E)

            save_result = False

        # FIXME
        logging.warning("%s Saver end: save_result=%s, url=%s", self.__class__.__name__, save_result, url)

        return save_result

    def item_saver(self, url: str, keys: object, finger: (list, tuple)) -> bool:
        self._pipe.write("\t".join([url, str(keys)] + [str(i) for i in finger]) + "\n")
        self._pipe.flush
        return True
