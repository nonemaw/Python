
import sys

class Saver():
    def __init__(self, save_pipe=sys.stdout):
        self._save_pipe = save_pipe

    def save_working(self, url:str, keys:object, item:(list, tuple)) -> bool:
        """
        working function, must "try, except" and don't change the parameters and return
        :return save_result: True or False
        """
        try:
            save_result = self.item_saver(url, keys, item)
        except Exception as excep:
            save_result = False
        return save_result

    def item_saver(self, url: str, keys: object, item: (list, tuple)) -> bool:
        self._save_pipe.write("\t".join([url, str(keys)] + [str(i) for i in item]) + "\n")
        self._save_pipe.flush
        return True
