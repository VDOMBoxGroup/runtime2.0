"""Write a response body to the socket in bounded blocks.

`shutil.copyfileobj` reads `shutil.COPY_BUFSIZE` at a time, and that constant is
**one mebibyte on Windows** against 64 KiB everywhere else. A 984 KB file
therefore went out in a single read and a single write.

Measured on this server, the same every time: 978 944 bytes reached the client -
exactly 239 x 4096 - then nothing, and the connection died 19 seconds later.
Four attempts in five, always at the same byte, with and without HTTP/1.1: the
protocol had nothing to do with it. The WebDAV path of the same server, which
writes in 64 KiB blocks, serves two mebibytes without trouble.

What made the defect expensive was not the cut but the **silence**: the server
announced 984 200 bytes, delivered fewer, and nothing said so anywhere. The
client concluded a network fault, the server log carried nothing, and a
truncated file settled into the browser cache. Hence the check below, which
speaks.
"""

BLOCK = 65536


def write_in_blocks(source, sink, announced=None, where="", trace=None):
    """Copy `source` into `sink` block by block. Return the bytes written.

    `announced` is the length told to the client, when it is known: a source
    that stops short must leave a trace, not a blank. `trace` is the logging
    function to use - `debug` at the call site - because this module must not
    depend on the caller's.
    """
    written = 0
    try:
        while True:
            block = source.read(BLOCK)
            if not block:
                break
            sink.write(block)
            written += len(block)
    except Exception as error:
        if trace:
            trace("Response interrupted after %d bytes on %s: %s: %s"
                  % (written, where, type(error).__name__, error))
        raise

    if announced is not None and written != announced and trace:
        trace("TRUNCATED BODY on %s: %d bytes written for %d announced "
              "(the source stopped before the end)" % (where, written, announced))
    return written
