#!/usr/bin/env python3
# Copyright (c) 2021-2024 oatsu
"""
USTの促音を含むノートを分割する。
その際、LABファイルの中のclの時刻に合わせる。
"""
from copy import deepcopy
from datetime import datetime
from glob import glob
from os import makedirs
from os.path import basename, dirname, isfile, join, splitext
from shutil import copy2
from typing import List

import utaupy


def compare_lab_and_ust(ust: utaupy.ust.Ust, lab: utaupy.label.Label, table: dict):
    """
    音素が一致するか調べる。
    """
    ust_phonemes = utaupy.utils.ustobj2songobj(ust, table).as_mono()
    for idx, (ph_lab, ph_ust) in enumerate(zip(lab, ust_phonemes)):
        if ph_lab.symbol != ph_lab.symbol:
            raise ValueError(
                f'{idx} 番目の音素が一致しません。(lab: {ph_lab.symbol}, ust: {ph_ust.symbol})')


def get_cl_ratio_list(ust: utaupy.ust.Ust, lab_align: utaupy.label.Label, table: dict
                      ) -> List[float]:
    """
    ノートの時間のうちclが占める比率を計算する。
    その比率のリストを返す。
    """
    lab_score = utaupy.utils.ustobj2songobj(ust, table).as_mono()
    # DEBUG
    # lab_score.write('score.full')
    # 促音だけを取り出す。
    cl_phonemes_align = [
        phoneme for phoneme in lab_align if phoneme.symbol == 'cl']
    cl_phonemes_score = [
        phoneme for phoneme in lab_score if phoneme.symbol == 'cl']

    assert len(cl_phonemes_align) == len(cl_phonemes_score), '長さが一致しません'

    cl_ratio_list = []
    for cl_align, cl_score in zip(cl_phonemes_align, cl_phonemes_score):
        # clを含むノートの長さ
        note_duration = cl_score.end - cl_score.start
        # clの発声時間
        cl_duration = cl_align.end - cl_align.start

        # ノートのうちのclの割合
        cl_ratio = cl_duration / note_duration
        cl_ratio_list.append(cl_ratio)

    # NOTE: 歌詞が「っ」のノートが含まれると、正常なUSTだとしても
    #       負の値や1より大きい値を取りうるためチェック昨日を無効。
    # clの占める比率が変な値でないことを確認する。
    # assert all(0 <= t <= 1 for t in cl_ratio_list)

    return cl_ratio_list


def devide_cl(ust, label, table):
    """
    clが含まれているノートを、ラベルを基準にして分割する。
    """
    # 音素が一致することを確認する。
    compare_lab_and_ust(ust, label, table)
    # ノートの長さに占める促音の比率のリストを取得する。
    cl_ratio_list = get_cl_ratio_list(ust, label, table)

    # 促音の出現回数が一致することを確認する
    cl_notes = [note for note in ust.notes if 'っ' in note.lyric]
    if len(cl_notes) != len(cl_ratio_list):
        raise ValueError(
            f'UST内の促音数({len(cl_notes)}) と LAB内の促音数{len(cl_ratio_list)} が一致しません。')

    # UST加工後のノートのリスト
    new_notes = []
    # 促音の出現回数を数える
    idx_cl = 0
    for note in ust.notes:
        if note.lyric == 'っ':
            cl_ratio = cl_ratio_list[idx_cl]
            # NOTE: 後でprintを消す↓
            print(note.lyric, cl_ratio)
            new_notes.append(note)
            # カウントを進める
            idx_cl += 1
        elif 'っ' in note.lyric:
            cl_ratio = cl_ratio_list[idx_cl]
            # NOTE: 後でprintを消す↓
            print(note.lyric, cl_ratio)
            new_note = deepcopy(note)
            new_note.lyric = new_note.lyric.replace('っ', '')
            new_note.length = round(new_note.length * (1 - cl_ratio))
            # 半分にした時の長さが2.5とかになった時は2.4を経由して2にする
            cl_note = deepcopy(note)
            cl_note.lyric = 'っ'
            cl_note.length = round(cl_note.length * cl_ratio)
            cl_note.tag = '[#INSERT]'
            # ノートを追加
            new_notes.append(new_note)
            new_notes.append(cl_note)
            # カウントを進める
            idx_cl += 1
        else:
            new_notes.append(note)
    ust.notes = new_notes


def main():
    """
    ファイル指定して処理
    """
    # フォルダまたはファイルを指定
    ust_dir = input('USTファイルまたはフォルダを指定してください。\n>>> ').strip('"')
    lab_dir = input('LABファイルまたはフォルダを指定してください。\n>>> ').strip('"')
    path_table = join(dirname(__file__),
                      'kana2phonemes_002_oto2lab.table').strip('"')
    # ファイルを一括取得
    ust_files = [ust_dir] if isfile(ust_dir) else glob(
        join(ust_dir, '**', '*.ust'), recursive=True)
    lab_files = [lab_dir] if isfile(lab_dir) else glob(
        join(lab_dir, '**', '*.lab'), recursive=True)
    # ファイル数が一致していることを確認する
    if len(ust_files) != len(lab_files):
        raise ValueError(
            f'USTファイル数({len(ust_files)}) と LABファイル数({len(lab_files)}) が一致しません。')

    # かな→音素変換テーブルを読み取る
    table = utaupy.table.load(path_table)
    # バックアップフォルダを作る
    backup_dir = join(dirname(__file__), 'backup',
                      datetime.now().strftime('%Y-%m-%d-%H%M%S'))
    makedirs(backup_dir)
    # USTファイルを書き換える
    for path_ust, path_lab in zip(ust_files, lab_files):
        print('---------------------------------')
        print(path_ust)
        print(path_lab)
        if splitext(basename(path_ust))[0] != splitext(basename(path_lab))[0]:
            raise ValueError('USTとLABのファイル名が一致しません。')
        # USTファイルをバックアップ
        copy2(path_ust, join(backup_dir, basename(path_ust)))
        # LABファイルをバックアップ
        copy2(path_lab, join(backup_dir, basename(path_lab)))
        # 各ファイルを読み取る
        ust = utaupy.ust.load(path_ust)
        label = utaupy.label.load(path_lab)
        # Ustオブジェクトの中の促音を分割
        devide_cl(ust, label, table)
        # USTファイルを上書き
        ust.write(path_ust)
        print('---------------------------------')


if __name__ == '__main__':
    main()
    input('\nPress enter to exit.')
