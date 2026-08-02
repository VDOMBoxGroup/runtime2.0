# TODO — VDOM Runtime fixes & improvements

> Analysis performed on 2026-06-17 on the `dev_py3` branch (Python 3 port in progress).
> Test environment: conda `vdom` / Python 3.11.15. Server started and working on the
> nominal path (HTTP 200, header `VDOM v3 server 3.0.1 Python/3.11.15`).
>
> Priorities: **P0** blocker · **P1** security · **P2** robustness/quality · **P3** architecture/perf · **P4** tooling.

---

## P0 — Finish the Python 3 port

The server starts, but several modules are disabled or untested. The "heavy" paths
(vscript/js2py under real conditions, SOAP, WebDAV, emails) have not been exercised.

- [ ] **Re-enable the `mailing/` module** — manager disabled in `sources/server.py:21,46`
      (`# from mailing import VDOM_email_manager`). The code compiles under Py3 (see below);
      investigate why it stays disabled and reintegrate it after testing (the `dev_py3` commit
      mentions "smtp module ported").
- [ ] **Re-enable the `scheduler`** — `sources/server.py:45` (`# managers.register("scheduler_manager", …)`).
- [ ] **Re-enable `file_share`** if needed — `sources/server.py:31`.
- [ ] **(Verified) No Py2 *syntax* residues**: `python -m compileall sources` passes with
      **0 errors** under Python 3.11. No `.iteritems()`/`.has_key()`/`basestring`/`xrange`
      in the code; the few `except X, e:` and `unicode(...)` are in **comments**.
      → Still useful: run `pyupgrade --py311-plus` (already a dep) for *semantic* modernization
      (idioms, f-strings), but this is not a blocker.
- [ ] **Exercise the untested subsystems**: real execution of vscript + js2py
      (`scripting/wrappers/server.py`), SOAP admin API (`soap/server.py`), WebDAV sharing
      (`webdav_server/`). This is where the remaining Py2 regressions are hiding.
- [ ] **Address the 161 `TODO/FIXME/XXX/HACK` markers** spread across 59 files
      (hotspots: `memory/application/builder.py`, `file_access/manager.py`,
      `scripting/wrappers/application.py`, `soap/server.py`). Triage and create tickets.

## P0 — C extension build

- [ ] **Document/automate the build of `memory/vdomxml/_loads`** (`memory/vdomxml/loads.c`).
      The build fails without **Microsoft C++ Build Tools** (MSVC 14+). Today the Python fallback
      (`loads.py`) takes over → functionally OK, but a performance loss when loading large
      applications.
      → Option A: ship a prebuilt wheel. Option B: document the Build Tools installation.
      Option C: commit to the Python fallback and drop the extension if the gain is not critical.
- [ ] **Fix the `manage.py build` action**: it does not exist in the action list
      (`argparse` rejects `build`) although the README mentions it. Either add it, or update the README.

---

## P1 — Security

- [ ] **Remove hardcoded secrets from the code**:
  - `sources/settings.py:105` — `OVH_LOGGING_TOKEN = "3d01766a-…"` (cleartext token, committed).
  - `sources/security/user_manager.py` — default admin account `Admin` / cleartext password.
  → Externalize to environment variables / a non-versioned config file (`settings.ini`).
  → **Rotate** the OVH token and the admin password (already exposed in git history).
- [ ] **Force changing default passwords** (`root`, `Admin`, empty `guest`) on first startup.
- [ ] **Review the default listening port = 80** (`settings.py:11`) and the lack of native TLS.
      Recommendation: deploy behind a reverse proxy (TLS, rate limiting).
- [ ] **Review the SOAP admin surface** (`soap/server.py`): make sure every sensitive method
      really goes through `__check_session()` + ACL, not just some of them.
- [ ] **Review the SOAP session-key mechanism** (`scripting/soap/soaputils.py`): "home-grown"
      iterative hash (modulo/inversion/XOR) — should be replaced with a standard HMAC.
- [ ] **Dynamic code execution**: `exec`/`eval` in the vscript pipeline and `js2py`
      (`vscript/extensions/evalstring.py`, `scripting/wrappers/server.py`). Verify that no
      untrusted user input reaches them.

---

## P2 — Robustness & code quality

- [ ] **Reduce bare `except:`** — **75 occurrences across 22 files** (e.g. `web/http_request_handler.py` ×8,
      `web/wsgi_request_handler.py` ×7, `memory/manager.py` ×15). They hide real errors
      (including `KeyboardInterrupt`/`SystemExit`). → Target specific exceptions and log them.
- [ ] **Replace thread killing via asynchronous exception** — `ScriptManager` uses
      `PyThreadState_SetAsyncExc()` (`scripting/manager.py`) for timeouts. Unreliable mechanism
      (does not apply inside C code, may leave resources locked).
      → Investigate a cooperative model (deadline checking) or subprocess isolation.
- [ ] **Set up automated tests beyond vscript** — only `vscript/tests/` is provided
      (~30 files). Add integration tests: server startup, app install/select,
      end-to-end HTTP request, SOAP, WebDAV.
- [ ] **Integrate `ruff`** (already a dev dependency) in CI + pre-commit to lock the style and
      catch Py2 regressions.
- [ ] **Logging**: `LOGGING_OUTPUT=True` captures stdout/stderr; verify it does not swallow
      tracebacks useful for diagnosis.

---

## P3 — Architecture, dependencies & performance

- [ ] **Rationalize the SOAP libraries** — 4 stacks coexist in the deps:
      `soappy-py3`, `zeep`, `suds`, `wstools-py3`. Identify the one actually used
      (the server relies on SOAPpy) and drop the others.
- [ ] **Clarify the use of `peewee` and `redis`** — declared in `pyproject.toml` but the
      actual persistence uses **raw SQLite** (`storage/`, `database/`). Either integrate them,
      or remove them from the dependencies.
- [ ] **Thread-per-connection concurrency model** (`socketserver.ThreadingTCPServer`,
      `web/http_server.py`): limits scalability. Evaluate switching to the **WSGI** deployment
      already present (`server/wsgi.py`) behind an application server (gunicorn/waitress/uvicorn).
- [ ] **`js2py` dependency = Python 3.11 lock-in** — `js2py` does not support Python 3.12+
      (crashes on import). As long as it is required, the env is frozen at 3.11.
      → Evaluate an alternative (PyMiniRacer / quickjs / dropping js2py) to be able to upgrade.
- [ ] **Deprecated `pkg_resources`** — runtime warning (via SOAPpy). Track the deprecation
      (removal announced) and pin `setuptools<81` short-term if needed.

---

## P4 — Tooling & developer experience

- [x] **Launch script** — `run-server.bat` created at the root (`cd sources && python server.py %*`).
- [ ] **Full bootstrap script**: create/activate the conda env `vdom` (Python 3.11) +
      `pip install -r requirements.vdom.txt` + `manage.py deploy`, in a single script.
- [ ] **Update the `README.md`**: outdated install instructions
      (mentions `pycrypto`, `WsgiDAV==2.4.0`, `python manage.py build`). Document the real
      procedure: conda 3.11 → deps → `deploy` → `server.py`.
- [ ] **Provide a demo application** (`.xml`) + an `install`/`select` script
      to validate end-to-end rendering (currently "Application not found" by default).
- [ ] **Freeze reproducible dependencies**: `requirements.vdom.txt` was generated manually
      from `pyproject.toml`. Verify its consistency with `poetry.lock` (the source of truth).

---

## Context notes

- **Shallow clone**: the repository was fetched with `--depth=1` (`dev_py3` branch only).
  Run `git fetch --unshallow` to get the full history before any serious work.
- **Corporate SSL**: git uses `http.sslBackend=schannel`; conda needs `CONDA_SSL_VERIFY=false`
  and poetry fails over the network (install done via pip). Keep this in mind for CI.
