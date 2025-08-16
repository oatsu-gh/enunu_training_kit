#!/usr/bin/env python3
# Copyright (c) 2022 oatsu
"""
指定したwavファイルまたは
指定したフォルダあるwavファイルを
時間方向に反転して上書きする。
"""
import warnings
from glob import glob
from os.path import isfile, join, splitext

from tqdm import tqdm

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import pydub


def reverse_wavfile(path_in, path_out):
    """
    指定したWAVファイルを時間方向に反転して出力する。
    """
    # 拡張子に対応した形式で音声ファイルを読みとる。
    ext_in = splitext(path_in)[1].strip('.')
    sound = pydub.AudioSegment.from_file(path_in, format=ext_in)
    # 反転して保存
    ext_out = splitext(path_out)[1].strip('.')
    sound.reverse().export(path_out, format=ext_out)


def main():
    """
    一括変換する。
    """
    path = input('Select WAV directory or WAV file: ').strip('"')

    # 指定したパスがファイルなら1要素のリストにする。
    if isfile(path):
        wav_files = [path]
    # 指定したパスがフォルダなら再帰的に検索してリストにする。
    else:
        wav_files = glob(join(path, '**', '*.wav'), recursive=True)

    # 全ファイルを反転して上書き
    for path_wav in tqdm(wav_files):
        reverse_wavfile(path_wav, path_wav)


if __name__ == "__main__":
    main()
