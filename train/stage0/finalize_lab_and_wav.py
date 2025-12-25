#!/usr/bin/env python3
# Copyright (c) 2021-2025 oatsu
"""
各種ラベルが正常かチェックして、
timelag とか duration とか acoustic の学習用フォルダにコピーする。
あと音声ファイルを切断する。

音声の offset_correction がよくわからんので実装できてない。
"""

import warnings
from functools import partial
from glob import glob
from os import makedirs
from os.path import basename, expanduser, splitext
from shutil import copy
from sys import argv

import utaupy as up
import yaml
from natsort import natsorted
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from pydub import AudioSegment


def lab_fix_offset(path_lab):
    """
    ラベルの開始時刻をゼロにする。(音声を切断したため。)
    ファイルは上書きする。
    offset: 最初に余裕をどのくらい持たせるか[100ns]
    """
    label = up.label.load(path_lab)
    # どのくらいずらすか
    dt = label[0].start
    for phoneme in label:
        phoneme.start -= dt
        phoneme.end -= dt
    label.write(path_lab)


def prepare_data_for_timelag_models(
    full_align_round_seg_files: list, full_score_round_seg_files: list, timelag_dir
):
    """
    timilagモデル用にラベルファイルをコピーする

    Shiraniさんのレシピではoffset_correstionの工程が含まれるが、
    このプログラムでは実装していない。
    """
    label_phone_align_dir = f'{timelag_dir}/label_phone_align'
    label_phone_score_dir = f'{timelag_dir}/label_phone_score'

    makedirs(label_phone_align_dir, exist_ok=True)
    makedirs(label_phone_score_dir, exist_ok=True)

    # 手動設定したフルラベルファイルを複製
    print('Copying full_align_round_seg files')
    for path_lab in tqdm(full_align_round_seg_files):
        copy(path_lab, f'{label_phone_align_dir}/{basename(path_lab)}')

    # 楽譜から生成したフルラベルファイルを複製
    print('Copying full_score_round_seg files')
    for path_lab in tqdm(full_score_round_seg_files):
        copy(path_lab, f'{label_phone_score_dir}/{basename(path_lab)}')


def prepare_data_for_duration_models(full_align_round_seg_files: list, duration_dir):
    """
    durationモデル用にラベルファイルを複製する。
    """
    label_phone_align_dir = f'{duration_dir}/label_phone_align'
    makedirs(label_phone_align_dir, exist_ok=True)

    # 手動設定したフルラベルファイルを複製
    print('Copying full_align_round_seg files')
    for path_lab_in in tqdm(full_align_round_seg_files):
        path_lab_out = f'{label_phone_align_dir}/{basename(path_lab_in)}'
        copy(path_lab_in, path_lab_out)
        lab_fix_offset(path_lab_out)


def _segment_one_wav(path_wav, acoustic_wav_dir, full_align_round_seg_files):
    """1つのWAVファイルを処理（並列処理用）"""
    songname = splitext(basename(path_wav))[0]

    # 対応するセグメントファイルを取得
    corresponding_full_align_round_seg_files = [
        path for path in full_align_round_seg_files if f'{songname}__seg' in path
    ]

    # 音声ファイルを読み取る
    wav = AudioSegment.from_file(path_wav, format='wav')
    for path_lab in corresponding_full_align_round_seg_files:
        label = up.label.load(path_lab)
        # 切断時刻を取得
        t_start_ms = round(label[0].start / 10000)
        t_end_ms = round(label[-1].end / 10000)
        # 切り出す
        wav_slice = wav[t_start_ms:t_end_ms]
        # outdir/songname_segx.wav
        path_wav_seg_out = f'{acoustic_wav_dir}/{splitext(basename(path_lab))[0]}.wav'
        wav_slice.export(path_wav_seg_out, format='wav')


def prepare_data_for_acoustic_models(
    full_align_round_seg_files: list,
    full_score_round_seg_files: list,
    wav_files: list,
    acoustic_dir: str,
):
    """
    acousticモデル用に音声ファイルとラベルファイルを複製する。
    """
    wav_dir = f'{acoustic_dir}/wav'
    label_phone_align_dir = f'{acoustic_dir}/label_phone_align'
    label_phone_score_dir = f'{acoustic_dir}/label_phone_score'
    # 出力先フォルダを作成
    makedirs(wav_dir, exist_ok=True)
    makedirs(label_phone_align_dir, exist_ok=True)
    makedirs(label_phone_score_dir, exist_ok=True)

    # wavファイルを分割して保存する
    print('Split wav files (parallel)')
    # 並列用に引数を部分適用
    func = partial(
        _segment_one_wav,
        acoustic_wav_dir=wav_dir,
        full_align_round_seg_files=full_align_round_seg_files,
    )
    # 並列処理で実行
    process_map(func, wav_files, colour='blue')

    # 手動設定したフルラベルファイルを複製
    print('Copying full_align_round_seg files')
    for path_lab_in in tqdm(full_align_round_seg_files):
        path_lab_out = f'{label_phone_align_dir}/{basename(path_lab_in)}'
        copy(path_lab_in, path_lab_out)
        lab_fix_offset(path_lab_out)

    # 楽譜から生成したフルラベルファイルを複製
    print('Copying full_score_round_seg files')
    for path_lab_in in tqdm(full_score_round_seg_files):
        path_lab_out = f'{label_phone_score_dir}/{basename(path_lab_in)}'
        copy(path_lab_in, path_lab_out)
        lab_fix_offset(path_lab_out)


def main(path_config_yaml):
    """
    フォルダを指定して全体の処理をやる
    """
    with open(path_config_yaml, encoding='utf-8') as fy:
        config = yaml.safe_load(fy)
    out_dir = expanduser(config['out_dir'])

    full_align_round_seg_files = natsorted(glob(f'{out_dir}/full_align_round_seg/*.lab'))
    full_score_round_seg_files = natsorted(glob(f'{out_dir}/full_score_round_seg/*.lab'))
    wav_files = natsorted(glob(f'{out_dir}/wav/*.wav', recursive=True))

    # フルラベルをtimelag用のフォルダに保存する。
    print('Preparing data for timelag models')
    timelag_dir = f'{out_dir}/timelag'
    prepare_data_for_timelag_models(
        full_align_round_seg_files, full_score_round_seg_files, timelag_dir
    )

    # フルラベルのオフセット修正をして、duration用のフォルダに保存する。
    print('Preparing data for duration models')
    duration_dir = f'{out_dir}/duration'
    prepare_data_for_duration_models(full_align_round_seg_files, duration_dir)

    # フルラベルのオフセット修正をして、acoustic用のフォルダに保存する。
    # wavファイルをlabファイルのセグメントに合わせて切断
    # wavファイルの前後にどのくらい余白を設けるか
    print('Preparing data for acoustic models')
    acoustic_dir = f'{out_dir}/acoustic'
    prepare_data_for_acoustic_models(
        full_align_round_seg_files, full_score_round_seg_files, wav_files, acoustic_dir
    )


if __name__ == '__main__':
    if len(argv) == 1:
        main('config.yaml')
    else:
        main(argv[1].strip('"'))
