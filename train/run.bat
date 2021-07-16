@ REM Copyright (c) 2021 oatsu
@ echo off

REM HOW TO USE -----------------
REM .\run.bat 0 7
REM ----------------------------

REM SETTING ---------------------------------------------
set python=.\..\python-3.8.10-embed-amd64\python.exe
set start_stage=%1
set stop_stage=%2

echo python      : %python%
echo start_stage : %start_stage%
echo stop_stage  : %stop_stage%
REM -----------------------------------------------------


if not defined python (
    set python=python
)


if %start_stage% leq 0 if %stop_stage% geq 0 (
    echo "stage 0: Data preparation"
    rmdir /s /q data dump
    .\bat\data_preparation.bat
)


if %start_stage% leq 1 if %stop_stage% geq 1 (
    echo "stage 1: Feature generation"
)


if %start_stage% leq 2 if %stop_stage% geq 2 (
    echo "stage 2: Training time-lag model"
)


if %start_stage% leq 3 if %stop_stage% geq 3 (
    echo "stage 3: Training duration model"
)


if %start_stage% leq 4 if %stop_stage% geq 4 (
    echo "stage 4: Training acoustic model"
)


if %start_stage% leq 5 if %stop_stage% geq 5 (
    echo "stage 5: Generate features"
)


if %start_stage% leq 6 if %stop_stage% geq 6 (
    echo "stage 6: Synthesis waveforms"
)


if %start_stage% leq 6 if %stop_stage% geq 6 (
    echo "stage 7: Copy models to release directory"
    %python% prepare_model_for_release_enunu.py
)
