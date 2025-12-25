@REM train timelag and acoustic models
.\PortableGit-2.52.0\bin\bash.exe .\run.sh --stage 2 --stop_stage 3
@REM train acoustic model
.\PortableGit-2.52.0\bin\bash.exe .\run.sh --stage 4 --stop_stage 4

PAUSE
