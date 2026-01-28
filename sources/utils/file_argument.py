import os
import builtins


class File_argument:
    def __init__(self, fileobj, name):
        """File argument wrapper for uploaded files"""
        self.fileobj = fileobj
        self.name = self.__try_decode(name)
        self.autoremove = True

    def __getitem__(self, key):
        if not isinstance(key, int):
            raise TypeError
        if key == 0:
            self.fileobj.seek(0)
            value = self.fileobj.read()
            self.fileobj.seek(0)
            return value
        elif key == 1:
            return self.name
        else:
            raise AttributeError

    def __try_decode(self, item):
        if isinstance(item, bytes):
            return bytes(item).decode("utf-8", "ignore")
        else:
            return item

    def remove(self):
        """Remove uploaded file from HDD"""
        if self.fileobj:
            filepath = getattr(self.fileobj, "name", None)
            if not self.fileobj.closed:
                self.fileobj.close()
            if filepath:
                try:
                    os.remove(filepath)
                except Exception as e:
                    debug(e.message)
            self.fileobj = None  # TODO: maybe not none bug StringIO()?

    def close(self):
        """Close file object and give name"""
        self.fileobj.close()
        return getattr(self.fileobj, "name")


class Attachment:
    def __init__(self, file_argument):
        self.__filearg = file_argument

    def __get_filename(self):
        return self.__filearg.name

    def __get_handler(self):
        fh = self.__filearg.fileobj
        if fh.closed:
            fh = open(fh.name, mode="rb")
            self.__filearg.fileobj = fh
        return self.__filearg.fileobj

    def _get_realpath(self):
        return getattr(self.__filearg.fileobj, "name", None)

    def _del_fileobj(self):
        self.__filearg.fileobj = None

    def remove(self):
        self.__filearg.remove()

    name = property(__get_filename)
    handler = property(__get_handler)


# TODO: Try to avoid this
builtins.Attachment = Attachment
