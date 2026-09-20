"""What this server is, and which build of it is running.

SERVER_VERSION is the product version. It has read "3.0.1" for years - a
constant, derived from nothing - which is fine for a name and useless for the
only question anyone asks of a running site: does it carry the fix?

Measured on 2026-09-20, four production sites and the development machine all
answered

    Server: VDOM v3 server 3.0.1 Python/3.11.16

while the development machine was thirty-three commits ahead of them, carrying
HTTP/1.1, the finished WebDAV port and the block writer that none of the others
had. The header could not tell them apart, so nobody could - and the only way
to answer "is the WebDAV fix deployed here?" was to find someone who remembered.

SERVER_BUILD answers it, the way LimeOS already answers it for the application:
`git describe --tags --always --dirty`, resolved once at import.

Three sources, in order:

* the `BUILD` file beside `sources/`, written by the image build. This is what
  a container has - there is no git checkout inside one.
* `git describe`, for a development machine running from a clone.
* `UNKNOWN_BUILD` otherwise - and it says so rather than inventing a number.
  The application learned that one the hard way: a build that could not name
  itself shipped as `0.0.0-source`, went into service, and the site could no
  longer say what it was running.

For the image build, one line is enough, before the sources are copied in:

    git describe --tags --always --dirty > BUILD
"""

import os
import subprocess

REPOSITORY_VERSION = str(0o001)
SERVER_VERSION = "3.0.%s" % REPOSITORY_VERSION

UNKNOWN_BUILD = "unknown-build"

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STAMP = os.path.join(_ROOT, "BUILD")


def _stamped():
    """What the image build wrote, if it wrote anything."""
    try:
        with open(_STAMP, "r", encoding="utf-8") as handle:
            return handle.read().strip() or None
    except OSError:
        return None


def _described():
    """What git says, when we are running from a clone.

    Never raises and never waits long: this runs at import, on every start, and
    a server that cannot start because `git` is missing would be a poor trade
    for a version string.
    """
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always", "--dirty"],
            cwd=_ROOT, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    return result.stdout.strip() or None


SERVER_BUILD = _stamped() or _described() or UNKNOWN_BUILD

SERVER_NAME = "VDOM Server " + SERVER_VERSION
