#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
指定したフォルダ内の全USTに対して、
全ノートのフラグを全部消して、新しい値で上書きする
"""

from glob import glob

import utaupy
from tqdm import tqdm


def USTファイルのフラグを上書きする(USTファイルのパス, 新しいフラグ):
    """
    指定したUSTファイルのフラグを上書きする。
    """
    ust = utaupy.ust.load(USTファイルのパス)
    for note in ust.notes:
        note.flags = 新しいフラグ
    ust.write(USTファイルのパス)


def main():
    """
    全体の処理を実行
    """
    USTがあるフォルダ = input('処理対象のUSTがあるフォルダを指定してください\n>>> ').strip('"')
    新しいフラグ = input('新しく設定したいフラグを入力してください\n>>> ')
    処理対象の全USTファイルのパス = glob(f'{USTがあるフォルダ}/**/*.ust', recursive=True)

    for USTファイルのパス in tqdm(処理対象の全USTファイルのパス):
        USTファイルのフラグを上書きする(USTファイルのパス, 新しいフラグ)

    input('終わりました。エンターを押すと閉じます。')


if __name__ == '__main__':
    main()
