#!/usr/bin/env python3
# Copyright (c) 2021-2025 oatsu
"""
モノラベルを休符周辺で切断する。
pau の直前で切断する。休符がすべて結合されていると考えて実行する。
"""

from functools import partial
from glob import glob
from os import makedirs
from os.path import basename, splitext
from sys import argv
from typing import Union

import utaupy as up
import yaml
from natsort import natsorted  # pyright: ignore[reportMissingImports]
from tqdm.contrib.concurrent import process_map
from utaupy.hts import HTSFullLabel
from utaupy.label import Label


def all_phonemes_are_rest(label: Union[Label, HTSFullLabel]) -> bool:
    """
    フルラベルまたはモノラベル中に休符しかないかどうか判定
    """
    rests = {'pau', 'sil'}
    # 全部の音素が休符であるか否か
    return all(phoneme.symbol in rests for phoneme in label)


def split_mono_label_short(label: Label) -> list[Label]:
    """
    モノラベルを分割する。分割後の複数のLabelからなるリストを返す。
    """
    new_label = Label()
    result = [new_label]

    new_label.append(label[0])
    for phoneme in label[1:-1]:
        if phoneme.symbol == 'pau':
            new_label = Label()
            result.append(new_label)
        new_label.append(phoneme)
    # 最後の音素を追加
    new_label.append(label[-1])
    return result


def split_mono_label_middle(label: Label, frequency) -> list[Label]:
    """
    モノラベルを分割する。分割後の複数のLabelからなるリストを返す。
    pauが10回出現するたびに分割する。
    """
    if frequency <= 0:
        raise ValueError('Argument "frequency" must be positive integer.')

    new_label = Label()
    result = [new_label]
    new_label.append(label[0])

    # pauが出現する回数をカウントする
    counter = 0
    for phoneme in label[1:-1]:
        if phoneme.symbol == 'pau':
            counter += 1
            # pauが出現してfrequency回目のとき
            if counter == frequency:
                new_label = Label()
                result.append(new_label)
                # 回数をリセット
                counter = 0
        new_label.append(phoneme)
    # 最後の音素を追加
    new_label.append(label[-1])
    return result


def split_mono_label_long(label: Label) -> list[Label]:
    """
    モノラベルを分割する。分割後の複数のLabelからなるリストを返す。
    [pau][pau], [pau][sil] のいずれかの並びで切断する。
    """
    new_label = Label()
    result = [new_label]

    new_label.append(label[0])
    for i, current_phoneme in enumerate(label[1:-1]):
        previous_phoneme = label[i - 1]
        if (previous_phoneme.symbol, current_phoneme.symbol) in [
            ('pau', 'sil'),
            ('pau', 'pau'),
        ]:
            new_label = Label()
            result.append(new_label)
        new_label.append(current_phoneme)
    # 最後の音素を追加
    new_label.append(label[-1])
    return result


def split_full_label_short(full_label: HTSFullLabel) -> list:
    """
    フルラベルを分割する。
    できるだけコンテキストを保持するため、SongではなくHTSFullLabelで処理する。
    """
    new_label = HTSFullLabel()
    new_label.append(full_label[0])
    result = [new_label]
    for oneline in full_label[1:-1]:
        if oneline.phoneme.identity == 'pau':
            new_label = HTSFullLabel()
            result.append(new_label)
        new_label.append(oneline)
    # 最後の行を追加
    new_label.append(full_label[-1])
    # 休符だけの後奏部分があった場合は直前のラベルにまとめる。
    if len(result) >= 2 and all_phonemes_are_rest(result[-1]):
        result[-2] += result[-1]
        del result[-1]
    return result


def split_full_label_middle(full_label: HTSFullLabel, frequency: int) -> list[HTSFullLabel]:
    """
    モノラベルを分割する。分割後の複数のLabelからなるリストを返す。
    pauが10回出現するたびに分割する。
    """
    if frequency <= 0:
        raise ValueError('Argument "frequency" must be positive integer.')
    new_label = HTSFullLabel()
    result = [new_label]

    new_label.append(full_label[0])
    # pauが出現する回数をカウントする
    counter = 0
    for oneline in full_label[1:-1]:
        if oneline.phoneme.identity == 'pau':
            counter += 1
            if counter == frequency:
                new_label = HTSFullLabel()
                result.append(new_label)
                counter = 0
        new_label.append(oneline)
    # 最後の行を追加
    new_label.append(full_label[-1])
    # 休符だけの後奏部分があった場合は直前のラベルにまとめる。
    if len(result) >= 2 and all_phonemes_are_rest(result[-1]):
        result[-2] += result[-1]
        del result[-1]
    return result


def split_full_label_long(full_label: HTSFullLabel) -> list:
    """
    フルラベルを分割する。
    できるだけコンテキストを保持するため、SongではなくHTSFullLabelで処理する。

    split_full_label_short ではうまく学習できなかった。
    そこで、全部の休符で切ったらさすがに短かったので長めにとる。
    [pau][pau], [pau][sil] のいずれかの並びで切断する。
    """
    new_label = HTSFullLabel()
    new_label.append(full_label[0])
    result = [new_label]

    for oneline in full_label[1:-1]:
        if (oneline.previous_phoneme.identity, oneline.phoneme.identity) in [
            ('pau', 'sil'),
            ('pau', 'pau'),
        ]:
            print(oneline.previous_phoneme.identity, oneline.phoneme.identity)
            new_label = HTSFullLabel()
            result.append(new_label)
        new_label.append(oneline)
    # 最後の行を追加
    new_label.append(full_label[-1])

    # 休符だけの後奏部分があった場合は直前のラベルにまとめる。
    if len(result) >= 2 and all_phonemes_are_rest(result[-1]):
        result[-2] += result[-1]
        del result[-1]
    return result


def split_label(
    label: Union[Label, HTSFullLabel], mode: str, middle_frequency: int
) -> list[Union[Label, HTSFullLabel]]:
    """
    ラベルを分割してリストにして返す。フルラベルとモノラベルを自動で使い分ける。
    mode: 'short' か 'long' のいずれか
    """
    if mode not in ('short', 'middle', 'long'):
        raise ValueError('Argument "mode" must be "short" or "long".')
    result = ''
    if isinstance(label, Label):
        if mode == 'short':
            result = split_mono_label_short(label)
        elif mode == 'middle':
            result = split_mono_label_middle(label, middle_frequency)
        elif mode == 'long':
            result = split_mono_label_long(label)
    elif isinstance(label, HTSFullLabel):
        if mode == 'short':
            result = split_full_label_short(label)
        elif mode == 'middle':
            result = split_full_label_middle(label, middle_frequency)
        elif mode == 'long':
            result = split_full_label_long(label)
    return result


def remove_zensou_and_kousou(path_lab) -> None:
    """
    長すぎてGPUメモリを食いつぶすような音素を除去(前奏、間奏、後奏とか)
    """
    label = up.label.load(path_lab)
    label.data = label.data[1:-1]
    label.write(path_lab)


def process_label_file(path, out_dir, mode, frequency, file_type) -> None:
    """ラベルファイルを処理する共通関数

    Args:
        path: 処理対象ファイルのパス
        out_dir: 出力ディレクトリ
        mode: セグメンテーションモード
        frequency: セグメンテーション頻度
        file_type: ファイルタイプ ('full_score_round', 'full_align_round', 'mono_score_round', 'mono_align_round')
    """
    songname = splitext(basename(path))[0]

    # ファイルタイプに応じてラベルをロード
    if file_type.startswith('full'):
        label = up.hts.load(path)
    else:  # mono
        label = up.label.load(path)

    # セグメント化と保存
    for idx, segment in enumerate(split_label(label, mode, frequency)):
        path_out = f'{out_dir}/{file_type}_seg/{songname}__seg{idx}.lab'

        # ファイルタイプに応じて書き込み
        if file_type.startswith('full'):
            segment.write(path_out, strict_sinsy_style=False)  # pyright: ignore[reportCallIssue]
        else:  # mono
            segment.write(path_out)


def main(path_config_yaml, max_workers=None) -> None:
    """
    ラベルファイルを取得して分割する。（並列処理版）

    Args:
        path_config_yaml: 設定ファイルのパス
        max_workers: 並列処理の最大ワーカー数
    """
    with open(path_config_yaml, encoding='utf-8') as fy:
        config = yaml.safe_load(fy)
    out_dir = config['out_dir']
    mode = config['segmentation_mode']
    frequency = config['segmentation_frequency']

    # ファイル一覧を取得
    full_score_round_files = natsorted(glob(f'{out_dir}/full_score_round/*.lab'))
    mono_score_round_files = natsorted(glob(f'{out_dir}/mono_score_round/*.lab'))
    full_align_round_files = natsorted(glob(f'{out_dir}/full_align_round/*.lab'))
    mono_align_round_files = natsorted(glob(f'{out_dir}/mono_align_round/*.lab'))

    # 出力ディレクトリを作成
    makedirs(f'{out_dir}/full_score_round_seg', exist_ok=True)
    makedirs(f'{out_dir}/full_align_round_seg', exist_ok=True)
    makedirs(f'{out_dir}/mono_score_round_seg', exist_ok=True)
    makedirs(f'{out_dir}/mono_align_round_seg', exist_ok=True)

    # ファイルタイプごとの設定
    file_configs = [
        ('full_score_round', full_score_round_files),
        ('full_align_round', full_align_round_files),
        ('mono_score_round', mono_score_round_files),
        ('mono_align_round', mono_align_round_files),
    ]

    # 各ファイルタイプを並列処理
    for file_type, file_list in file_configs:
        # ファイルが見つからない場合はエラーを出力
        if not file_list:
            raise FileNotFoundError(f'No {file_type} label files found in {out_dir}/{file_type}/')
        print(f'Segmenting {file_type} label files')
        # 共通処理関数に必要なパラメータを部分適用
        process_func = partial(
            process_label_file,
            out_dir=out_dir,
            mode=mode,
            frequency=frequency,
            file_type=file_type,
        )
        process_map(
            process_func, file_list, max_workers=max_workers, desc=file_type, colour='blue'
        )


if __name__ == '__main__':
    if len(argv) == 1:
        main('config.yaml')
    else:
        main(argv[1].strip('"'))
