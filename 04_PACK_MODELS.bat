@REM pack trained models
@REM before packing, you need to edit "vocoder_eval_checkpoint" in config.yaml .
.\PortableGit-2.52.0\bin\bash.exe .\run.sh --stage 99 --stop_stage 99

PAUSE
