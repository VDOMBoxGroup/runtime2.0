import os
import tempfile
import builtins


class File_argument:
    def __init__(self, fileobj, name):
        """File argument wrapper for uploaded files"""
        self.fileobj = self.__spool(fileobj)
        self.name = self.__try_decode(name)
        self.autoremove = True

    def __spool(self, fileobj):
        """Guarantee the upload is a named file on disk.

        cgi.FieldStorage only calls make_file() once an upload passes 1000
        bytes; below that it keeps the content in a BytesIO, which has no
        .name. Everything downstream assumes there is one - Attachment reopens
        the file by name once the request that received it is over, and remove()
        deletes it by path. Under Python 2 that assumption held often enough to
        go unnoticed; under Python 3 a small upload reached Attachment as a
        closed BytesIO and raised

            AttributeError: '_io.BytesIO' object has no attribute 'name'

        from inside the application's exception handler, so the upload failed
        with no file stored and a success notification on screen.

        Spooling here makes the two paths identical whatever the size.
        """
        if getattr(fileobj, "name", None) is not None:
            return fileobj
        # VDOM_CONFIG is injected into builtins by startup, as request.py uses it
        spooled = tempfile.NamedTemporaryFile(
            "w+b", prefix="vdomupload", dir=VDOM_CONFIG["TEMP-DIRECTORY"],  # noqa: F821
            delete=False)
        try:
            fileobj.seek(0)
            spooled.write(fileobj.read())
        finally:
            spooled.flush()
            fileobj.close()
        spooled.seek(0)
        return spooled

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
                    # py3: BaseException.message is gone - reporting the failure
                    # must not itself raise AttributeError
                    debug(str(e))  # noqa: F821
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
