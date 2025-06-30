#!/usr/bin/env python3
# Copyright (c) 2021-2025 oatsu
"""
WAVファイルが full_align_lab より長いことを確認する（concurrent.futures 使用）。
"""
import warnings
from concurrent.futures import ProcessPoolExecutor
from glob import glob
from logging import warning
from os.path import join
from sys import argv

import utaupy
import yaml
from natsort import natsorted
from tqdm import tqdm

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from pydub import AudioSegment


def check_wav_and_lab_pair(paths: tuple[str, str]) -> str | None:
    """
    WAVとLABのペアを受け取り、WAVが短ければ警告メッセージを返す。
    """
    path_wav, path_lab = paths

    try:
        # LABファイルの最後の音素の時刻を取得 [sec]
        label = utaupy.label.load(path_lab)
        lab_endtime_sec = label[-1].end / 10000000

        # WAVファイルの長さを取得 [sec]
        wav_length_sec = AudioSegment.from_file(
            path_wav, 'wav').duration_seconds

        if wav_length_sec < lab_endtime_sec:
            return f'WAV is shorter than LAB or score. ({path_wav}) ({path_lab})'

    except Exception as e:
        return f'Error comparing files: {path_wav}, {path_lab} - {str(e)}'

    return None


def compare_wav_and_lab_parallel(wav_dir_in, lab_dir_in):
    """
    concurrent.futures を使って並列に比較
    """
    wav_files = natsorted(glob(f'{wav_dir_in}/*.wav'))
    lab_files = natsorted(glob(f'{lab_dir_in}/*.lab'))

    pairs = list(zip(wav_files, lab_files))
    if not pairs:
        warning(f'No files found in {wav_dir_in} or {lab_dir_in}')
        return

    warnings_found = []

    # マルチプロセスまたはマルチスレッドで処理する。
    with ProcessPoolExecutor() as executor:
        results = list(tqdm(
            executor.map(check_wav_and_lab_pair, pairs),
            total=len(pairs)
        ))
        warnings_found = [r for r in results if r]

    for msg in warnings_found:
        warning(msg)


def main(path_config_yaml):
    """
    configを読み取ってフォルダを指定し、全体の処理を実行する。
    """
    print('Asserting WAV files are longer than full_align_round label files')
    with open(path_config_yaml, 'r', encoding='utf-8') as fy:
        config = yaml.load(fy, Loader=yaml.FullLoader)

    out_dir = config['out_dir']
    wav_dir_in = join(out_dir, 'wav')
    full_align_dir_in = join(out_dir, 'full_align_round')
    full_score_dir_in = join(out_dir, 'full_score_round')

    print('Comparing length of LAB and WAV')
    compare_wav_and_lab_parallel(wav_dir_in, full_align_dir_in)

    print('Comparing length of score and WAV')
    compare_wav_and_lab_parallel(wav_dir_in, full_score_dir_in)


if __name__ == '__main__':
    if len(argv) == 1:
        main('config.yaml')
    else:
        main(argv[1].strip('"'))
