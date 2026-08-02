@echo off
rem VDOM Runtime - lancement du serveur
rem L'interpreteur est fige explicitement : ne pas dependre du PATH,
rem qui peut pointer vers un autre environnement conda.
set "VDOM_PY=%USERPROFILE%\.conda\envs\vdom311\python.exe"

if not exist "%VDOM_PY%" (
    echo [ERREUR] Environnement introuvable : %VDOM_PY%
    echo Creer l'environnement avec :
    echo     set CONDA_SSL_VERIFY=false
    echo     conda create -n vdom311 python=3.11 -y
    echo     "%%VDOM_PY%%" -m pip install -r requirements.vdom.txt
    exit /b 1
)

cd sources
"%VDOM_PY%" server.py %*
