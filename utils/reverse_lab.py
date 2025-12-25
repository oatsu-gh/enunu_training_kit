#!/usr/bin/env python3
# Copyright (c) 2022 oatsu
"""
指定したLABファイルまたは指定したフォルダにあるLABファイルを
時間方向に反転して上書きする。
WAVがLABより長いとラベル位置が狂うので注意。
"""
from glob import glob
from os.path import isfile, join, splitext

import utaupy
from tqdm import tqdm


def reverse_labfile(path_in, path_out):
    """
    指定したLABファイルの時系列を反転して出力する。
    """
    label = utaupy.label.load(path_in)
    # 最後の音素の発声終了時刻を取得する。
    # global_start = label[0].start
    global_end = label[-1].end
    # 時刻を反転したラベルを新規作成する。
    new_label = utaupy.label.Label()
    for phoneme in label:
        new_phoneme = utaupy.label.Phoneme()
        new_phoneme.symbol = phoneme.symbol
        new_phoneme.start = global_end - phoneme.end
        new_phoneme.end = global_end - phoneme.start
        new_label.append(new_phoneme)
    # 音素の並び順を逆にする。
    new_label.data.reverse()
    # 保存
    new_label.write(path_out)


def main():
    path = input('Select LAB directory or LAB file: ').strip('"')
    # 指定したパスがファイルなら1要素のリストにする。
    if isfile(path):
        lab_files = [path]
    # 指定したパスがフォルダなら再帰的に検索してリストにする。
    else:
        lab_files = glob(join(path, '**', '*.lab'), recursive=True)
    # 全ファイルを反転して上書き
    for path_lab in tqdm(lab_files):
        assert splitext(path_lab)[1] == '.lab'
        reverse_labfile(path_lab, path_lab)


if __name__ == "__main__":
    main()
