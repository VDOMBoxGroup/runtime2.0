
class LogFormatter(object):

    def __init__(self, name):
        self._name = name

    def format(self, *values):
        raise NotImplementedError

    def finditer(self, data):
        raise NotImplementedError

    def parse(self, data):
        raise NotImplementedError
