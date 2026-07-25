@setlocal
@set python_dir=%~dp0python-3.12.10-embed-amd64\

start http://localhost:6006
%python_dir%scripts\tensorboard.exe --logdir .\tensorboard

@endlocal
PAUSE
