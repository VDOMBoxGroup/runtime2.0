"""What this server is, and which build of it is running.

Both answers come from one string, and that string comes from git.

SERVER_VERSION read "3.0.1" for years - a constant, derived from nothing. It
survived the whole Python 3 portage, HTTP/1.1, the WebDAV rewrite and the block
writer without moving once, so the number said nothing about what a site was
running. Measured on 2026-09-20, four production sites and this machine all
answered

    Server: VDOM v3 server 3.0.1 Python/3.11.16

while this machine was thirty-four commits ahead of them. The header could not
tell them apart, so nobody could.

So the version is a **tag**, the way LimeOS already does it for the application:

    git tag 3.1.0 && git push origin 3.1.0

`git describe` then names every build after that tag, and `SERVER_VERSION` is
read back out of the name:

    3.1.0                  the tagged commit itself      -> 3.1.0
    3.1.0-34-g9884ca6      thirty-four commits past it   -> 3.1.0.34
    3.1.0-34-g9884ca6-dirty  ... with local edits        -> 3.1.0.34

The fourth component is the distance to the release, so the number moves on
every commit instead of waiting for someone to remember to bump it. It is the
build's own count, not a decision.

`--match` keeps this to tags shaped `X.Y.Z`. The repository also carries
`portage-1.2` and ticket tags like `10441`, and a version named after a ticket
would be worse than a constant.

SERVER_BUILD is the full describe string, headers and all, so `(3.1.0.34)` in
the version still resolves to one commit: `(3.1.0-34-g9884ca6)`.

Three sources, in order:

* the `BUILD` file beside `sources/`, written by the image build. This is what
  a container has - there is no git checkout inside one.
* `git describe`, for a development machine running from a clone.
* `UNKNOWN_BUILD` otherwise - and it says so rather than inventing a number.
  The application learned that one the hard way: a build that could not name
  itself shipped as `0.0.0-source`, went into service, and the site could no
  longer say what it was running.

For the image build, one line is enough, before the sources are copied in:

    git describe --tags --match '[0-9]*.[0-9]*.[0-9]*' --always --dirty > BUILD

Until the first `X.Y.Z` tag exists, nothing above can name a version and
SERVER_VERSION falls back to FALLBACK_VERSION - the number this server has
always answered. Landing this file changes no site's version on its own; the
tag does.
"""

import os
import re
import subprocess

#: What to answer when no version tag is reachable. This is the number every
#: site has answered since 3.0 shipped, so a build with no tag keeps saying
#: what it always said instead of claiming something new.
FALLBACK_VERSION = "3.0.1"

#: Only tags shaped X.Y.Z name a version. A glob, not a regexp: it is handed
#: to `git describe --match`.
VERSION_TAG_GLOB = "[0-9]*.[0-9]*.[0-9]*"

UNKNOWN_BUILD = "unknown-build"

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STAMP = os.path.join(_ROOT, "BUILD")

#: `3.1.0`, or `3.1.0-34-g9884ca6`, with an optional `-dirty` behind it.
_DESCRIBED = re.compile(r"^(\d+\.\d+\.\d+)(?:-(\d+)-g[0-9a-f]+)?(?:-dirty)?$")


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
            ["git", "describe", "--tags", "--match", VERSION_TAG_GLOB,
             "--always", "--dirty"],
            cwd=_ROOT, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    return result.stdout.strip() or None


def _version_of(build):
    """The version a describe string names, or None if it names none.

    A bare sha names none - that is a build whose history holds no version tag,
    and it gets the fallback rather than a number invented on the spot.
    """
    found = _DESCRIBED.match(build or "")
    if not found:
        return None
    release, distance = found.group(1), found.group(2)
    return "%s.%s" % (release, distance) if distance else release


SERVER_BUILD = _stamped() or _described() or UNKNOWN_BUILD
SERVER_VERSION = _version_of(SERVER_BUILD) or FALLBACK_VERSION

#: Kept for the callers that still read it. It is the patch component of the
#: version and no longer a constant anyone edits.
REPOSITORY_VERSION = SERVER_VERSION.split(".", 2)[-1]

SERVER_NAME = "VDOM Server " + SERVER_VERSION
