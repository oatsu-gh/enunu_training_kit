@REM --------------------------------
@REM Install PyTorch CPU version
@REM --------------------------------
set python_dir=%~dp0python-3.12.10-embed-amd64\

@REM Uninstall existing torch packages
%python_dir%python.exe -m pip uninstall torch torchaudio torchvision -y
@REM Remove "torch" and "~orch" directories
for /d %%D in ("%python_dir%Lib\site-packages\?orch") do rmdir /s /q "%%D" 2>NUL
for /d %%D in ("%python_dir%Lib\site-packages\?orchaudio") do rmdir /s /q "%%D" 2>NUL
for /d %%D in ("%python_dir%Lib\site-packages\?orchvision") do rmdir /s /q "%%D" 2>NUL

@REM Install CPU versions of torch packages
%python_dir%python.exe -m pip install torch torchaudio torchvision --no-warn-script-location

PAUSE
