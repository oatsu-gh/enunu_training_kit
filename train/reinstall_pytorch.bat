@echo off
set PYTHON_EXE=.\python-3.9.13-embed-amd64\python.exe

%PYTHON_EXE% -m pip install --upgrade pip wheel setuptools --no-warn-script-location
%PYTHON_EXE% -m pip install --upgrade light-the-torch --no-warn-script-location
%PYTHON_EXE% -m pip uninstall -y torch torchaudio --no-warn-script-location
%PYTHON_EXE% -m light-the-torch install --upgrade torch torchaudio

pause
