#!/usr/bin/env python3
# Copyright (c) 2021-2025 oatsu
"""
フルラベルを読み取ってモノラベルにして保存する。
"""

from functools import partial
from glob import glob
from os import makedirs
from os.path import basename, join
from sys import argv

import utaupy as up
import yaml
from tqdm.contrib.concurrent import process_map


def _convert_one_full_to_mono(path_full, mono_lab_dir):
    """1つのフルラベルをモノラベルに変換（並列処理用）"""
    full_label_obj = up.hts.load(path_full)
    full_label_obj.as_mono().write(join(mono_lab_dir, basename(path_full)))


def main(path_config_yaml):
    """
    configファイルからフォルダを指定して、全体の処理を実行する。
    """
    # 設定ファイルを読み取る
    with open(path_config_yaml, encoding='utf-8') as fy:
        config = yaml.safe_load(fy)

    # 入出力pathを指定
    out_dir = config['out_dir'].strip('"')
    full_score_dir = join(out_dir, 'full_score_round')
    mono_score_dir = join(out_dir, 'mono_score_round')

    # フルラベルファイル一覧を取得
    full_labels = glob(f'{full_score_dir}/*.lab')
    makedirs(mono_score_dir, exist_ok=True)

    print(f'Converting full-score to mono-score: {full_score_dir} -> {mono_score_dir}')
    # 並列処理用の関数を作成
    convert_func = partial(_convert_one_full_to_mono, mono_lab_dir=mono_score_dir)
    # 並列処理で実行
    process_map(convert_func, full_labels, colour='blue')


if __name__ == '__main__':
    main(argv[1].strip('"'))
