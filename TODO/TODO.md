# TODO — Corrections & améliorations du VDOM Runtime

> Analyse réalisée le 2026-06-17 sur la branche `dev_py3` (portage Python 3 en cours).
> Environnement de test : conda `vdom` / Python 3.11.15. Serveur démarré et fonctionnel
> sur le chemin nominal (HTTP 200, header `VDOM v3 server 3.0.1 Python/3.11.15`).
>
> Priorités : **P0** bloquant · **P1** sécurité · **P2** robustesse/qualité · **P3** archi/perf · **P4** outillage.

---

## P0 — Finir le portage Python 3

Le serveur démarre, mais plusieurs modules sont désactivés ou non testés. Les chemins
« lourds » (vscript/js2py en conditions réelles, SOAP, WebDAV, emails) n'ont pas été exercés.

- [ ] **Réactiver le module `mailing/`** — manager désactivé dans `sources/server.py:21,46`
      (`# from mailing import VDOM_email_manager`). Le code compile sous Py3 (cf. ci-dessous) ;
      vérifier pourquoi il reste désactivé et le réintégrer après test (le commit `dev_py3`
      mentionne « smtp module ported »).
- [ ] **Réactiver le `scheduler`** — `sources/server.py:45` (`# managers.register("scheduler_manager", …)`).
- [ ] **Réactiver `file_share`** si nécessaire — `sources/server.py:31`.
- [ ] **(Vérifié) Pas de résidu de *syntaxe* Py2** : `python -m compileall sources` passe avec
      **0 erreur** sous Python 3.11. Aucun `.iteritems()`/`.has_key()`/`basestring`/`xrange`
      dans le code ; les rares `except X, e:` et `unicode(...)` sont en **commentaires**.
      → Reste utile : passer `pyupgrade --py311-plus` (déjà en dep) pour une modernisation
      *sémantique* (idiomes, f-strings), mais ce n'est pas bloquant.
- [ ] **Exercer les sous-systèmes non testés** : exécution réelle de vscript + js2py
      (`scripting/wrappers/server.py`), API SOAP d'admin (`soap/server.py`), partage WebDAV
      (`webdav_server/`). La syntaxe est OK, mais les erreurs *sémantiques* Py2→Py3
      (bytes/str, comportements de division, etc.) ne se révèlent qu'à l'exécution.
- [ ] **Traiter les 161 marqueurs `TODO/FIXME/XXX/HACK`** répartis dans 59 fichiers
      (concentrations : `memory/application/builder.py`, `file_access/manager.py`,
      `scripting/wrappers/application.py`, `soap/server.py`). Trier et créer des tickets.

## P0 — Build de l'extension C

- [ ] **Documenter/automatiser le build de `memory/vdomxml/_loads`** (`memory/vdomxml/loads.c`).
      Le build échoue sans **Microsoft C++ Build Tools** (MSVC 14+). Aujourd'hui le fallback
      Python (`loads.py`) prend le relais → OK fonctionnellement, mais perte de perf au chargement
      des grosses applications.
      → Option A : fournir un wheel précompilé. Option B : documenter l'installation des Build Tools.
      Option C : assumer le fallback Python et retirer l'extension si le gain n'est pas critique.
- [ ] **Corriger l'action `manage.py build`** : elle n'existe pas dans la liste des actions
      (`argparse` rejette `build`) alors que le README l'indique. Soit l'ajouter, soit mettre à jour le README.

---

## P1 — Sécurité

- [ ] **Retirer les secrets en dur du code** :
  - `sources/settings.py:105` — `OVH_LOGGING_TOKEN = "3d01766a-…"` (token en clair, versionné).
  - `sources/security/user_manager.py` — compte admin par défaut `Admin` / mot de passe en clair.
  → Externaliser vers variables d'environnement / fichier de config non versionné (`settings.ini`).
  → **Rotation** du token OVH et du mot de passe admin (déjà exposés dans l'historique git).
- [ ] **Forcer le changement des mots de passe par défaut** (`root`, `Admin`, `guest` vide) au premier démarrage.
- [ ] **Auditer le port d'écoute par défaut = 80** (`settings.py:11`) et l'absence de TLS natif.
      Recommandation : déployer derrière un reverse-proxy (TLS, limites de débit).
- [ ] **Revue de la surface SOAP d'admin** (`soap/server.py`) : vérifier que toutes les méthodes
      sensibles passent bien par `__check_session()` + ACL, pas seulement certaines.
- [ ] **Revue du mécanisme de clé de session SOAP** (`scripting/soap/soaputils.py`) : hash itératif
      « maison » (modulo/inversion/XOR) — à remplacer par un HMAC standard.
- [ ] **Exécution de code dynamique** : `exec`/`eval` dans le pipeline vscript et `js2py`
      (`vscript/extensions/evalstring.py`, `scripting/wrappers/server.py`). Vérifier qu'aucune
      entrée utilisateur non maîtrisée n'y parvient.

---

## P2 — Robustesse & qualité de code

- [ ] **Réduire les `except:` nus** — **75 occurrences dans 22 fichiers** (ex. `web/http_request_handler.py` ×8,
      `web/wsgi_request_handler.py` ×7, `memory/manager.py` ×15). Ils masquent les vraies erreurs
      (y compris `KeyboardInterrupt`/`SystemExit`). → Cibler des exceptions précises et logguer.
- [ ] **Remplacer le kill de threads par exception asynchrone** — `ScriptManager` utilise
      `PyThreadState_SetAsyncExc()` (`scripting/manager.py`) pour les timeouts. Mécanisme non garanti
      (ne s'applique pas dans du code C, peut laisser des ressources verrouillées).
      → Étudier un modèle coopératif (vérification de deadline) ou l'isolation par sous-processus.
- [ ] **Mettre en place les tests automatisés au-delà de vscript** — seul `vscript/tests/` est fourni
      (~30 fichiers). Ajouter des tests d'intégration : démarrage serveur, install/select d'app,
      requête HTTP de bout en bout, SOAP, WebDAV.
- [ ] **Intégrer `ruff`** (déjà en dépendance dev) en CI + pre-commit pour figer le style et
      attraper les régressions Py2.
- [ ] **Logging** : `LOGGING_OUTPUT=True` capture stdout/stderr ; vérifier qu'il n'avale pas
      les tracebacks utiles au diagnostic.

---

## P3 — Architecture, dépendances & performance

- [ ] **Rationaliser les bibliothèques SOAP** — 4 stacks coexistent dans les deps :
      `soappy-py3`, `zeep`, `suds`, `wstools-py3`. Identifier celle réellement utilisée
      (le serveur s'appuie sur SOAPpy) et retirer les autres.
- [ ] **Clarifier l'usage de `peewee` et `redis`** — déclarés dans `pyproject.toml` mais la
      persistance réelle utilise **SQLite brut** (`storage/`, `database/`). Soit les intégrer,
      soit les retirer des dépendances.
- [ ] **Modèle de concurrence thread-per-connection** (`socketserver.ThreadingTCPServer`,
      `web/http_server.py`) : limite la scalabilité. Évaluer une bascule vers le déploiement
      **WSGI** déjà présent (`server/wsgi.py`) derrière un serveur applicatif (gunicorn/waitress/uvicorn).
- [ ] **Dépendance `js2py` = verrou Python 3.11** — `js2py` ne supporte pas Python 3.12+
      (plante à l'import). Tant qu'il est requis, l'env est figé en 3.11.
      → Évaluer une alternative (PyMiniRacer / quickjs / sortie de js2py) pour pouvoir monter en version.
- [ ] **`pkg_resources` déprécié** — avertissement à l'exécution (via SOAPpy). Suivre la dépréciation
      (suppression annoncée) et épingler `setuptools<81` à court terme si besoin.

---

## P4 — Outillage & expérience développeur

- [x] **Script de lancement** — `run-server.bat` créé à la racine (`cd sources && python server.py %*`).
- [ ] **Script de bootstrap complet** : créer/activer l'env conda `vdom` (Python 3.11) +
      `pip install -r requirements.vdom.txt` + `manage.py deploy`, en un seul script.
- [ ] **Mettre à jour le `README.md`** : instructions d'installation obsolètes
      (mentionne `pycrypto`, `WsgiDAV==2.4.0`, `python manage.py build`). Documenter la vraie
      procédure : conda 3.11 → deps → `deploy` → `server.py`.
- [ ] **Fournir une application de démonstration** (`.xml`) + script `install`/`select`
      pour valider le rendu de bout en bout (actuellement « Application not found » par défaut).
- [ ] **Geler les dépendances reproductibles** : `requirements.vdom.txt` a été généré manuellement
      depuis `pyproject.toml`. Vérifier sa cohérence avec `poetry.lock` (source de vérité).

---

## Notes de contexte

- **Clone superficiel** : le dépôt a été récupéré avec `--depth=1` (branche `dev_py3` uniquement).
  Faire `git fetch --unshallow` pour disposer de l'historique complet avant tout travail sérieux.
- **SSL d'entreprise** : git utilise `http.sslBackend=schannel` ; conda nécessite `CONDA_SSL_VERIFY=false`
  et poetry échoue sur le réseau (installation faite via pip). À garder en tête pour la CI.
