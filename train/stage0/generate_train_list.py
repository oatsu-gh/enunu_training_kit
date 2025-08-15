#!/usr/bin/env python3
# Copyright (c) 2021-2025 oatsu
"""
eval.list と dev.list と train.list を生成する。
utt_list.txtは作らなくていい気がする。
data/list/eval.list
data/list/dev.list
data/list/train.list

全ファイルから12個おきにevalとdevに入れる。dev以外の全ファイルをtrainに入れる。
"""

from glob import glob
from os import makedirs
from os.path import basename, expanduser, join, splitext
from sys import argv

import yaml
from natsort import natsorted


def generate_train_list(out_dir, interval: int = 11) -> None:
    """
    utt.list
    eval.list
    dev.list
    train.list
    """
    if not 5 <= interval <= 20:
        msg = f'Interval must be between 5 and 20, got {interval}.'
        raise ValueError(msg)
    print(f'Generate train list: interval = {interval}')

    # 学習対象のファイル一覧を取得
    wav_dir = join(out_dir, 'acoustic', 'wav')
    utt_list = glob(f'{wav_dir}/*.wav')
    utt_list = natsorted([splitext(basename(path))[0] for path in utt_list])
    len_utt_list = len(utt_list)
    # utt_listが空でないことを確認
    if len_utt_list == 0:
        raise Exception(f'No wav files in "{wav_dir}".')

    # 各種曲名リストを作る
    dev_list = []
    eval_list = []
    train_list = []

    # segment レベルで dev,eval,train に分割する場合
    # for idx, songname in enumerate(utt_list):
    #     # dev は多めにする。interval=10 のとき 10%。
    #     if idx % interval == 0:
    #         dev_list.append(songname)
    #     # eval は少なめにする。interval=10 のとき 5%。
    #     elif idx % (interval * 2) == 1:
    #         eval_list.append(songname)
    #     # 残りは train_no_dev にする。interval=10 のとき 85%。
    #     else:
    #         train_list.append(songname)

    # 曲レベルで dev, eval, train に分割する場合、まずは曲ごとに utt_list 内のファイル名を
    d_songnames: dict[list] = {}
    for songname in utt_list:
        base_songname = songname.rsplit('__seg', 1)[0]
        if base_songname not in d_songnames:
            d_songnames[base_songname] = [songname]
        else:
            d_songnames[base_songname].append(songname)

    # dev, eval, train に分割する
    for idx, base_songname in enumerate(d_songnames.values()):
        # dev は多めにする。interval=10 のとき 10%。
        if idx % interval == 0:
            dev_list += base_songname
        # eval は少なめにする。interval=10 のとき 5%。
        elif idx % (interval * 2) == 1:
            eval_list += base_songname
        # 残りは train_no_dev にする。interval=10 のとき 85%。
        else:
            train_list += base_songname

    # すべてのリストの要素が 1以上であることを確認する
    if not dev_list:
        raise ValueError('Development list is empty.')
    if not eval_list:
        raise ValueError('Evaluation list is empty.')
    if not train_list:
        raise ValueError('Training list is empty.')

    # それぞれの割合を確認する
    total = len_utt_list
    eval_ratio = len(eval_list) / total * 100
    dev_ratio = len(dev_list) / total * 100
    train_ratio = len(train_list) / total * 100
    # 各リストの個数を5桁で右寄せ、比率を5.1fで表示し、表示位置を揃える
    print(f'Total: {total:5d} segs')
    print(f'eval : {len(eval_list):5d} segs ({eval_ratio:5.1f}%)')
    print(f'dev  : {len(dev_list):5d} segs ({dev_ratio:5.1f}%)')
    print(f'train: {len(train_list):5d} segs ({train_ratio:5.1f}%)')

    # リスト出力先フォルダを作成
    list_dir = join(out_dir, 'list')
    makedirs(list_dir, exist_ok=True)

    # ファイルの出力パス
    path_utt_list = join(list_dir, 'utt_list.txt')
    path_dev_list = join(list_dir, 'dev.list')
    path_eval_list = join(list_dir, 'eval.list')
    path_train_list = join(list_dir, 'train_no_dev.list')

    # ファイル出力
    with open(path_utt_list, mode='w', newline='\n') as f_utt:
        f_utt.write('\n'.join(utt_list))
    with open(path_dev_list, mode='w', newline='\n') as f_utt:
        f_utt.write('\n'.join(dev_list))
    with open(path_eval_list, mode='w', newline='\n') as f_utt:
        f_utt.write('\n'.join(eval_list))
    with open(path_train_list, mode='w', newline='\n') as f_utt:
        f_utt.write('\n'.join(train_list))

    # 結果を表示
    print('Generated train list:')
    print('- utt_list  :', path_utt_list)
    print('- dev_list  :', path_dev_list)
    print('- eval_list :', path_eval_list)
    print('- train_list:', path_train_list)


def main(path_config_yaml):
    """
    フォルダを指定して実行
    """
    with open(path_config_yaml) as fy:
        config = yaml.safe_load(fy)
    out_dir = expanduser(config['out_dir'])
    generate_train_list(out_dir)


if __name__ == '__main__':
    main(argv[1].strip('"'))
