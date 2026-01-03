@REM --------------------------------
@REM Install PyTorch using light-the-torch
@REM --------------------------------
@set python_dir=%~dp0python-3.12.10-embed-amd64\

@REM Uninstall existing torch packages
%python_dir%python.exe -m pip uninstall torch torchaudio torchvision -y
@REM Remove torch directories
@for /d %%D in ("%python_dir%Lib\site-packages\?orch") do rmdir /s /q "%%D" 2>NUL
@for /d %%D in ("%python_dir%Lib\site-packages\?orchaudio") do rmdir /s /q "%%D" 2>NUL
@for /d %%D in ("%python_dir%Lib\site-packages\?orchvision") do rmdir /s /q "%%D" 2>NUL

@REM Upgrade light-the-torch and install torch packages
%python_dir%python.exe -m pip install --upgrade light-the-torch --no-warn-script-location --disable-pip-version-check
%python_dir%python.exe -m light_the_torch install torch torchaudio torchvision --no-warn-script-location --disable-pip-version-check

PAUSE
