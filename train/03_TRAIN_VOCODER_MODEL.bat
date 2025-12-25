@REM prepare vocoder training data (stage1 is required in advance)
.\PortableGit-2.52.0\bin\bash.exe .\run.sh --stage 9 --stop_stage 9

@REM train vocoder (uSFGAN) model
.\PortableGit-2.52.0\bin\bash.exe .\run.sh --stage 11 --stop_stage 11

PAUSE
