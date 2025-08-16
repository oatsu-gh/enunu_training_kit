#!/usr/bin/env python3
# Copyright (c) 2025 oatsu
"""
ラベルを休符で分割する。

最初に長い休符で分割したのち、そのあと一定の長さまたは休符の出現回数ごとに分割する。
"""

from sys import argv
from pathlib import Path
import utaupy

from natsort import natsorted
from utaupy.label import Label
import yaml
from os import makedirs
from tqdm.contrib import tzip


def check_labfile_count_and_names(dirs: list[Path]):
    """指定したフォルダ内にあるラベルのファイル数やファイル名が一致するか確認する。

    dirs: ラベルファイルが格納されているフォルダのリスト
    """
    # 各フォルダのLABファイル一覧を取得する。2次元リスト。
    label_files = [natsorted(d.glob('*.lab')) for d in dirs]
    # ファイル数
    label_count = len(label_files[0])

    # ファイル数をチェック
    if not all(len(files) == label_count for files in label_files):
        raise ValueError('LABファイル数が一致しません。')

    # ファイル名をチェック
    for i in range(label_count):
        names = [files[i].stem for files in label_files]
        if len(set(names)) == 1:
            continue
        raise ValueError(f'ファイル名が一致しません: {names}')


def _segment_labels_at_pause(
    mono_score_label: Label,
    full_score_label: Label,
    mono_align_label: Label,
    full_align_label: Label,
    pauses: list[str],
) -> tuple[list[Label], list[Label], list[Label], list[Label]]:
    """休符直前でラベルを分割して、分割後のラベルのリストを返す。

    label: 分割対象のラベル
    """
    mono_score_segments = []
    full_score_segments = []
    mono_align_segments = []
    full_align_segments = []
    # 休符位置を確認
    pau_indices = [i for i, ph in enumerate(mono_score_label) if ph.symbol in pauses]
    # 休符直前～次の休符直前 でセグメントにする。最後の休符は無視される。
    for start_idx, end_idx in zip(pau_indices[:-1], pau_indices[1:]):
        mono_score_segments.append(mono_score_label[start_idx:end_idx])
        full_score_segments.append(full_score_label[start_idx:end_idx])
        mono_align_segments.append(mono_align_label[start_idx:end_idx])
        full_align_segments.append(full_align_label[start_idx:end_idx])
    return (mono_score_segments, full_score_segments, mono_align_segments, full_align_segments)


def split_label_objects(
    mono_score_label: Label,
    full_score_label: Label,
    mono_align_label: Label,
    full_align_label: Label,
    max_pause_duration: float,  # sec
    max_segment_length: float,  # sec
    pauses: list[str] = None,
) -> tuple[list[Label], list[Label], list[Label], list[Label]]:
    """ラベルを休符で分割する。

    休符の長さが一定以上の場合は必ず分割し、その休符を除去する。
    その後、休符の出現回数ごとに再度分割する。
    """
    # 休符扱いの音素一覧
    if pauses is None:
        pauses = ['pau', 'sil']

    # max_pause_duration と max_segment_length の単位をLABファイル用に換算する。
    max_pause_duration *= 1e7
    max_segment_length *= 1e7

    # 各LABファイルの音素数が一致するか、最初と最後の音素が休符であるかを確認する。
    phoneme_counts = [
        len(mono_score_label),
        len(full_score_label),
        len(mono_align_label),
        len(full_align_label),
    ]
    if len(set(phoneme_counts)) != 1:
        error_msg = f'各ラベル内の音素数 ({", ".join(map(str, phoneme_counts))}) が一致しません。'
        raise ValueError(error_msg)
    if mono_score_label[0].symbol not in pauses:
        raise ValueError(f'最初の音素が休符ではありません: {mono_score_label[0].symbol}')
    if mono_score_label[-1].symbol not in pauses:
        raise ValueError(f'最後の音素が休符ではありません: {mono_score_label[-1].symbol}')

    # 毎休符で分割したLabelのリストを作成する。
    (
        l_short_mono_score_segments,
        l_short_full_score_segments,
        l_short_mono_align_segments,
        l_short_full_align_segments,
    ) = _segment_labels_at_pause(
        mono_score_label, full_score_label, mono_align_label, full_align_label, pauses
    )

    # 各ラベルの分割後のリストを初期化
    l_mono_score_segments = []
    l_full_score_segments = []
    l_mono_align_segments = []
    l_full_align_segments = []

    # 結合用のラベルを初期化
    current_mono_score_seg = Label()
    current_full_score_seg = Label()
    current_mono_align_seg = Label()
    current_full_align_seg = Label()

    for (short_mono_score_seg, short_full_score_seg, short_mono_align_seg, short_full_align_seg) in zip(
        l_short_mono_score_segments, l_short_full_score_segments, l_short_mono_align_segments, l_short_full_align_segments
    ):  # fmt: skip
        # 現在のセグメントの長さを計算する。
        current_segment_length = sum(ph.duration for ph in current_mono_score_seg)
        # 開始の休符が基準より長い場合は、休符を除去してセグメントを新規作成する。
        if short_mono_score_seg[0].duration > max_pause_duration:
            # セグメントが空の場合はセグメント追加をスキップする。
            if len(current_mono_score_seg) > 0:
                l_mono_score_segments.append(current_mono_score_seg)
                l_full_score_segments.append(current_full_score_seg)
                l_mono_align_segments.append(current_mono_align_seg)
                l_full_align_segments.append(current_full_align_seg)
            current_mono_score_seg = short_mono_score_seg[1:]
            current_full_score_seg = short_full_score_seg[1:]
            current_mono_align_seg = short_mono_align_seg[1:]
            current_full_align_seg = short_full_align_seg[1:]
        # 開始の休符が基準よりも短いがセグメントを結合すると基準長を超える場合は、休符を除去せずにセグメントを新規作成する。
        elif (
            current_segment_length + sum(ph.duration for ph in short_mono_score_seg)
            > max_segment_length
        ):
            # セグメントが空の場合はセグメント追加をスキップする。
            if len(current_mono_score_seg) > 0:
                l_mono_score_segments.append(current_mono_score_seg)
                l_full_score_segments.append(current_full_score_seg)
                l_mono_align_segments.append(current_mono_align_seg)
                l_full_align_segments.append(current_full_align_seg)
            current_mono_score_seg = short_mono_score_seg
            current_full_score_seg = short_full_score_seg
            current_mono_align_seg = short_mono_align_seg
            current_full_align_seg = short_full_align_seg
        #  開始の休符が基準より短く、セグメントを結合しても基準長を超えない場合はセグメントを延長する。
        else:
            current_mono_score_seg.extend(short_mono_score_seg)
            current_full_score_seg.extend(short_full_score_seg)
            current_mono_align_seg.extend(short_mono_align_seg)
            current_full_align_seg.extend(short_full_align_seg)

    # 最後のセグメントを追加する
    l_mono_score_segments.append(current_mono_score_seg)
    l_full_score_segments.append(current_full_score_seg)
    l_mono_align_segments.append(current_mono_align_seg)
    l_full_align_segments.append(current_full_align_seg)

    # 各セグメントの音素数が一致しているか確認する。
    for mono_score_seg, full_score_seg, mono_align_seg, full_align_seg in zip(
        l_mono_score_segments,
        l_full_score_segments,
        l_mono_align_segments,
        l_full_align_segments,
    ):
        len_mono_score_seg = len(mono_score_seg)
        len_full_score_seg = len(full_score_seg)
        len_mono_align_seg = len(mono_align_seg)
        len_full_align_seg = len(full_align_seg)

        # 4種類のセグメントの音素数が一致しない場合はエラー
        if not (
            len_mono_score_seg == len_full_score_seg == len_mono_align_seg == len_full_align_seg
        ):
            error_msg = f'音素数が一致しません: {len_mono_score_seg}, {len_full_score_seg}, {len_mono_align_seg}, {len_full_align_seg}'
            raise ValueError(error_msg)
        if len_mono_score_seg <= 1:
            raise ValueError(f'音素数が少なすぎます: {len_mono_score_seg}')

    return (
        l_mono_score_segments,
        l_full_score_segments,
        l_mono_align_segments,
        l_full_align_segments,
    )


def main(path_config_yaml: Path) -> None:
    """全体の処理をする。

    ラベルの読み取り → 分割 → 保存
    """
    with open(path_config_yaml, encoding='utf-8') as fy:
        config = yaml.safe_load(fy)
    out_dir = Path(config['out_dir'])

    # 入力ファイル
    in_mono_score_round_dir = out_dir / 'mono_score_round'
    in_full_score_round_dir = out_dir / 'full_score_round'
    in_mono_align_round_dir = out_dir / 'mono_align_round'
    in_full_align_round_dir = out_dir / 'full_align_round'

    # LABファイル数とファイル名が揃っているか点検する。
    check_labfile_count_and_names(
        [
            in_mono_score_round_dir,
            in_full_score_round_dir,
            in_mono_align_round_dir,
            in_full_align_round_dir,
        ]
    )

    # 各フォルダのLABファイル一覧を取得する。
    in_mono_score_round_lab_files = natsorted(in_mono_score_round_dir.glob('*.lab'))
    in_full_score_round_lab_files = natsorted(in_full_score_round_dir.glob('*.lab'))
    in_mono_align_round_lab_files = natsorted(in_mono_align_round_dir.glob('*.lab'))
    in_full_align_round_lab_files = natsorted(in_full_align_round_dir.glob('*.lab'))

    # 出力ディレクトリをリストにまとめる。
    out_mono_score_round_seg_dir = out_dir / 'mono_score_round_seg'
    out_full_score_round_seg_dir = out_dir / 'full_score_round_seg'
    out_mono_align_round_seg_dir = out_dir / 'mono_align_round_seg'
    out_full_align_round_seg_dir = out_dir / 'full_align_round_seg'
    output_dirs = [
        out_mono_score_round_seg_dir,
        out_full_score_round_seg_dir,
        out_mono_align_round_seg_dir,
        out_full_align_round_seg_dir,
    ]
    # 出力フォルダを作成する
    for path in output_dirs:
        makedirs(path, exist_ok=True)

    # 各曲のラベルを分割してセグメント化し、ファイルとして保存する。
    for (
        orig_mono_score_path,
        orig_full_score_path,
        orig_mono_align_path,
        orig_full_align_path,
    ) in tzip(
        in_mono_score_round_lab_files,
        in_full_score_round_lab_files,
        in_mono_align_round_lab_files,
        in_full_align_round_lab_files,
        colour='blue',
    ):
        # LABファイルを読み取ってLabelオブジェクトを作成する。
        in_mono_score_lab = utaupy.label.load(orig_mono_score_path)
        in_full_score_lab = utaupy.label.load(orig_full_score_path)
        in_mono_align_lab = utaupy.label.load(orig_mono_align_path)
        in_full_align_lab = utaupy.label.load(orig_full_align_path)

        # Labelオブジェクトを分割してセグメント化する
        print()
        print(orig_mono_score_path.stem)
        mono_score_segments, full_score_segments, mono_align_segments, full_align_segments = (
            split_label_objects(
                in_mono_score_lab,
                in_full_score_lab,
                in_mono_align_lab,
                in_full_align_lab,
                max_pause_duration=config['max_pause_duration'],
                max_segment_length=config['max_segment_length'],
            )
        )
        # セグメントを保存する。その際、ファイル名は元のファイル名にセグメント番号を付加する。
        for idx, (mono_score_seg, full_score_seg, mono_align_seg, full_align_seg) in enumerate(
            zip(mono_score_segments, full_score_segments, mono_align_segments, full_align_segments)
        ):
            str_idx = str(idx).zfill(2)
            segment_name = f'{orig_mono_score_path.stem}__seg{str_idx}.lab'
            mono_score_seg.write(out_mono_score_round_seg_dir / segment_name)
            full_score_seg.write(out_full_score_round_seg_dir / segment_name)
            mono_align_seg.write(out_mono_align_round_seg_dir / segment_name)
            full_align_seg.write(out_full_align_round_seg_dir / segment_name)


if __name__ == '__main__':
    if len(argv) == 1:
        main(Path('config.yaml'))
    else:
        main(Path(argv[1].strip('"')))
