#!/usr/bin/env python3
# Copyright (c) 2021-2025 oatsu
"""
音声ファイルのフォーマットが適切か点検する。
- モノラル音声か
- 全部同じビット深度か
  - 16bit int または 32bit int か
- 全部同じサンプルレートか
  - config と対応しているか
"""

import logging
import warnings
from concurrent.futures import ProcessPoolExecutor
from glob import glob
from os.path import join
from statistics import mode
from sys import argv

import yaml
from natsort import natsorted
from tqdm.auto import tqdm

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from pydub import AudioSegment


def get_audio_info(path_wav):
    """
    各WAVファイルの情報を取得（並列実行される）
    """
    try:
        audio = AudioSegment.from_file(path_wav)
        return {
            'path': path_wav,
            'channels': audio.channels,
            'frame_rate': audio.frame_rate,
            'sample_width': audio.sample_width,
        }
    except Exception as e:
        logging.error('ファイル読み込みエラー: %s - %s', path_wav, str(e))
        return None


def check_all_wav_files(wav_dir_in):
    """
    全音声ファイルの情報を並列で取得し、検証する。

    Returns:
        tuple: (mono_ok, sample_rate_ok, bit_depth_ok)
    """
    wav_files = natsorted(glob(f'{wav_dir_in}/*.wav'))

    # ファイルが見つからない場合はすべてNGにする。
    if not wav_files:
        logging.error('WAVファイルが見つかりません: %s', wav_dir_in)
        return False, False, False

    # 並列処理: ProcessPoolExecutor を使用して get_audio_info を並列実行
    with ProcessPoolExecutor() as executor:
        # executor.map を tqdm でラップし、進捗バーを表示
        audio_info = list(
            tqdm(executor.map(get_audio_info, wav_files), total=len(wav_files))
        )

    # None（エラー）が含まれていないか
    if any(info is None for info in audio_info):
        return False, False, False

    # チャンネル数チェック（モノラル）
    mono_ok = True
    for info in audio_info:
        if info['channels'] != 1:
            logging.error('モノラル音声ではありません。: %s', info['path'])
            mono_ok = False

    # サンプリングレートチェック
    all_frame_rates = [info['frame_rate'] for info in audio_info]
    sample_rate_ok = True
    if len(set(all_frame_rates)) > 1:
        mode_frame_rate = mode(all_frame_rates)
        for info in audio_info:
            if info['frame_rate'] != mode_frame_rate:
                logging.error(
                    'サンプリングレートが他のファイルと一致しません。: %s', info['path']
                )
        sample_rate_ok = False

    # ビット深度チェック
    all_sample_widths = [info['sample_width'] for info in audio_info]
    bit_depth_ok = True
    if len(set(all_sample_widths)) > 1:
        mode_bit_depth = mode(all_sample_widths)
        for info in audio_info:
            if info['sample_width'] != mode_bit_depth:
                logging.error(
                    'ビット深度が他のファイルと一致しません。: %s', info['path']
                )
        bit_depth_ok = False

    return mono_ok, sample_rate_ok, bit_depth_ok


def main(path_config_yaml):
    """
    全体処理を実行する
    """
    print('Checking WAV files')

    with open(path_config_yaml, encoding='utf-8') as fy:
        config = yaml.safe_load(fy)

    out_dir = config['out_dir']
    wav_dir_in = join(out_dir, 'wav')

    mono_ok, sample_rate_ok, bit_depth_ok = check_all_wav_files(wav_dir_in)

    if not mono_ok:
        raise ValueError(
            'モノラルではない音声ファイルがあります。ログを確認して修正して下さい。'
        )
    if not sample_rate_ok:
        raise ValueError(
            'サンプリングレートが異なる音声ファイルがあります。ログを確認して修正して下さい。'
        )
    if not bit_depth_ok:
        raise ValueError(
            'ビット深度が異なる音声ファイルがあります。ログを確認して修正して下さい。'
        )

    print('All WAV files passed validation')


if __name__ == '__main__':
    if len(argv) == 1:
        main('config.yaml')
    else:
        main(argv[1].strip('"'))
