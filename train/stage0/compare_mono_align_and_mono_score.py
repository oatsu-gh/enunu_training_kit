#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
Sinsyの出力と音素数が一致するかだけをチェックする。
チェックに通過したら mono_label フォルダから mono_dtwフォルダにコピーする。

Shirani さんのレシピでは fastdtw を使って、
DB同梱のモノラベルをSinsy出力の音素と一致させる。
"""
import logging
import statistics
from glob import glob
from itertools import chain
# from os import makedirs
from os.path import basename
from sys import argv
from typing import List, Tuple, Union

import utaupy as up
import yaml
from natsort import natsorted
from tqdm import tqdm

VOWELS = {'a', 'i', 'u', 'e', 'o', 'A', 'I', 'U', 'E', 'O', 'N'}


def phoneme_is_ok(path_mono_align_lab, path_mono_score_lab):
    """
    音素数と音素記号が一致するかチェックする。
    """
    mono_align_label = up.label.load(path_mono_align_lab)
    mono_score_label = up.label.load(path_mono_score_lab)
    # 全音素記号が一致したらTrueを返す
    for mono_align_phoneme, mono_score_phoneme in zip(mono_align_label, mono_score_label):
        if mono_align_phoneme.symbol != mono_score_phoneme.symbol:
            error_message = '\n'.join([
                f'DB 동봉의 라벨과 악보에서 생성된 라벨의 음소기호가 일치하지 않습니다. ({basename(path_mono_align_lab)})',
                f'  DB동봉의 라벨  : {mono_align_phoneme}\t({path_mono_align_lab})',
                f'  악보의 라벨    : {mono_score_phoneme}\t({path_mono_score_lab})'
            ])
            logging.error(error_message)
            return False
    if len(mono_align_label) != len(mono_score_label):
        error_message = '\n'.join([
            f'DB동봉의 라벨과 악보에서 생성된 라벨의 음소 갯수가 일치하지 않습니다. ({basename(path_mono_align_lab)})',
            f'  DB동봉 라벨의 음소 갯수 : {len(mono_align_label)}\t({path_mono_align_lab})',
            f'  악보의 라벨의 음소 갯수 : {len(mono_score_label)}\t({path_mono_score_lab})'
        ])
        logging.error(error_message)
        return False
    return True


def force_start_with_zero(path_mono_align_lab):
    """
    最初の音素(pau)の開始時刻を0にする。
    LABの元のiniの、左ブランクとか先行発声が動かされてると0ではなくなってしまうため。
    """
    mono_align_label = up.label.load(path_mono_align_lab)
    if mono_align_label[0].start != 0:
        warning_message = \
            'DB동봉의 라벨의 첫 음소 개시 시각이 0이 아닙니다. 0으로 수정해서 처리를 진행해주세요. ({})'.format(
                basename(path_mono_align_lab))
        logging.warning(warning_message)
        mono_align_label[0].start = 0
        mono_align_label.write(path_mono_align_lab)


def calc_median_mean_pstdev(mono_align_lab_files: List[str],
                            mono_score_lab_files: List[str],
                            vowels=VOWELS
                            ) -> Tuple[int, int, int]:
    """
    ラベルと楽譜の母音のdurationの差の、統計値を求める。
    median: 中央値
    mean  : 平均値
    sigma : 標準偏差
    """
    # 全ラベルファイルを読み取る
    mono_align_label_objects = [up.label.load(path) for path in mono_align_lab_files]
    mono_score_label_objects = [up.label.load(path) for path in mono_score_lab_files]
    # Labelのリストを展開してPhonemeのリストにする
    mono_align_phonemes = list(chain.from_iterable(mono_align_label_objects))
    mono_score_phonemes = list(chain.from_iterable(mono_score_label_objects))
    # 母音以外を削除し、直後が休符なものも削除
    mono_align_phonemes = [
        phoneme for i, phoneme in enumerate(mono_align_phonemes[:-1])
        if (phoneme.symbol in vowels) and mono_align_phonemes[i + 1] not in ['cl', 'pau']
    ]
    mono_score_phonemes = [
        phoneme for i, phoneme in enumerate(mono_score_phonemes[:-1])
        if (phoneme.symbol in vowels) and mono_score_phonemes[i + 1] not in ['cl', 'pau']
    ]
    # durationの差の一覧
    duration_differences = [
        ph_align.duration - ph_score.duration
        for ph_align, ph_score in zip(mono_align_phonemes, mono_score_phonemes)
    ]
    # 中央値
    return (int(statistics.median(duration_differences)),
            int(statistics.mean(duration_differences)),
            int(statistics.pstdev(duration_differences)))


def offet_is_ok(path_mono_align_lab,
                path_mono_score_lab,
                mean_100ns: Union[int, float],
                stdev_100ns: Union[int, float],
                mode: str
                ) -> bool:
    """
    最初の音素の長さを比較して、閾値以上ずれていたらエラーを返す。
    threshold_ms の目安: 300ms-600ms (5sigma-10sigma)
    """
    k = {'strict': 5, 'medium': 6, 'lenient': 7}.get(mode, 6)
    # 単位換算して100nsにする
    upper_threshold = mean_100ns + k * stdev_100ns
    lower_threshold = mean_100ns - k * stdev_100ns
    # labファイルを読み込む
    mono_align_label = up.label.load(path_mono_align_lab)
    mono_score_label = up.label.load(path_mono_score_lab)
    # 設定した閾値以上差があるか調べる
    duration_difference = mono_align_label[0].duration - mono_score_label[0].duration
    if not lower_threshold < duration_difference < upper_threshold:
        warning_message = \
            'DB동봉의 라벨의 전주가 악보보다 {}ms 이상 빠르거나, {}ms 이상 깁니다. ({} ms) ({})'.format(
                round(lower_threshold / 10000),
                round(upper_threshold / 10000),
                round(duration_difference / 10000),
                basename(path_mono_align_lab)
            )
        logging.warning(warning_message)
        return False
    # 問題なければTrueを返す
    return True


def vowel_durations_are_ok(path_mono_align_lab,
                           path_mono_score_lab,
                           mean_100ns: Union[int, float],
                           stdev_100ns: Union[int, float],
                           mode: str,
                           vowels=VOWELS) -> bool:
    """
    母音の長さを比較して、楽譜中で歌詞ずれが起きていないかチェックする。
    閾値以上ずれていたら警告する。
    MIDIを自動生成するようなときに音素誤認識して、
    誤ったMIDIができてずれてることがあるのでその対策。

    threshold_ms の目安:  250 (5sigma-6sigma)
    - 優しめ: 6sigma
    - ふつう: 5sigma
    - 厳しめ: 4sigma
    """
    k = {'strict': 4, 'medium': 5, 'lenient': 6}.get(mode, 6)
    # 単位換算して100nsにする
    upper_threshold = mean_100ns + k * stdev_100ns
    lower_threshold = mean_100ns - k * stdev_100ns
    # labファイルを読み込む
    mono_align_label = up.label.load(path_mono_align_lab)
    mono_score_label = up.label.load(path_mono_score_lab)
    ok_flag = True
    # 休符を比較
    for i, (phoneme_align, phoneme_score) in enumerate(zip(mono_align_label[:-1], mono_score_label[:-1])):
        duration_difference = phoneme_align.duration - phoneme_score.duration
        if mono_align_label[i + 1].symbol in ['cl', 'pau']:
            continue
        if phoneme_align.symbol in vowels and not lower_threshold < duration_difference < upper_threshold:
            warning_message = '\n'.join([
                'DB동봉의 라벨이 악보에서 생성된 라벨의 모음보다 {} ms 이상 짧거나, {} ms 이상 깁니다. 평균치 ± {}σ 의 범위 밖 입니다. ({} ms) ({})'.format(
                    round(lower_threshold / 10000),
                    round(upper_threshold / 10000),
                    k,
                    round(duration_difference / 10000),
                    basename(path_mono_align_lab)),
                f'  직전 음소: {mono_align_label[i-1].symbol}',
                f'  DB동봉의 라벨 : {phoneme_align}\t({phoneme_align.duration / 10000} ms)\t{path_mono_align_lab}',
                f'  악보의 라벨   : {phoneme_score}\t({phoneme_score.duration / 10000} ms)\t{path_mono_score_lab}',
                f'  직전 음소: {mono_align_label[i+1].symbol}'
            ])
            logging.warning(warning_message)
            ok_flag = False
    return ok_flag


def main(path_config_yaml):
    """
    全体の処理をやる。
    """
    with open(path_config_yaml, 'r') as fy:
        config = yaml.load(fy, Loader=yaml.FullLoader)
    out_dir = config['out_dir']
    mono_align_files = natsorted(glob(f'{out_dir}/mono_align_round/*.lab'))
    mono_score_files = natsorted(glob(f'{out_dir}/mono_score_round/*.lab'))
    duration_check_mode = config['stage0']['vowel_duration_check']

    # mono_align_labの最初の音素が時刻0から始まるようにする。
    print('mono-align-LAB의 시작을 0으로 덮어씌웁니다.')
    for path_mono_align in tqdm(mono_align_files):
        force_start_with_zero(path_mono_align)

    # 音素記号や最初の休符の長さが一致するか確認する。
    print('mono-align-LAB과 mono-score-LAB을 비교 중...')
    invalid_basenames = []
    for path_mono_align, path_mono_score in zip(tqdm(mono_align_files), mono_score_files):
        if not phoneme_is_ok(path_mono_align, path_mono_score):
            invalid_basenames.append(basename(path_mono_align))

    # 母音のdurationの統計値を取得
    print('지속 시간 차이의 중위수, 평균 및 stdev 계산 중...')
    _, mean_100ns, stdev_100ns = calc_median_mean_pstdev(
        mono_align_files, mono_score_files)

    # 前奏の長さを点検
    print('첫 pau의 길이를 확인 중...')
    for path_mono_align, path_mono_score in zip(tqdm(mono_align_files), mono_score_files):
        if not offet_is_ok(path_mono_align, path_mono_score,
                           mean_100ns, stdev_100ns, mode=duration_check_mode):
            invalid_basenames.append(basename(path_mono_align))
    if len(invalid_basenames) > 0:
        raise Exception('DB에서 생성된 라벨과 악보에서 생성된 라벨에 부정합이 있습니다.'
                        '로그 파일을 참조하여 수정해주세요.')

    # 音素長をチェックする。
    print('mono-align-LAB 길이와 mono-score-LAB 길이를 비교 중...')
    for path_mono_align, path_mono_score in zip(tqdm(mono_align_files), mono_score_files):
        vowel_durations_are_ok(path_mono_align, path_mono_score,
                               mean_100ns, stdev_100ns, mode=duration_check_mode)


if __name__ == '__main__':
    main(argv[1].strip('"'))
