@REM check path (tensorflow does not support japanese path)
@powershell -NoProfile -Command "$path='%CD%'; if($path -match '[^\x00-\x7F]'){exit 1}else{exit 0}" >nul 2>&1
@if %errorlevel% neq 0 (
    echo === WARNING!! ================================================================================
    echo  Current directory path has non-ASCII characters like Japanese Hiragana, Katakana, or Kanji.
    echo  This will result errors. Rename the directory or run this in a different directory.
    echo ==============================================================================================
    exit /b 1
)
exit /b 0

@REM prepare vocoder training data (stage1 is required in advance)
.\PortableGit-2.52.0\bin\bash.exe .\run.sh --stage 9 --stop_stage 9

@REM train vocoder (uSFGAN) model
.\PortableGit-2.52.0\bin\bash.exe .\run.sh --stage 11 --stop_stage 11

PAUSE
