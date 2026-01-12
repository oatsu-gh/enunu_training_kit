#!/usr/bin/env python3
# Copyright (c) 2026 oatsu
"""
packed_models に作成されたモデルの、config.yaml に独自項目を追記する。
"""

import tomllib
from pathlib import Path
from sys import argv


def get_etk_version(path_toml: Path) -> str:
    """
    ETKのバージョンを取得する。
    """
    with open(path_toml, 'rb') as f:
        toml_dict = tomllib.load(f)
    return toml_dict['project']['version']


def main(
    path_config_yaml: Path | str,
    path_pyproject_toml: Path | str,
) -> str:
    """
    Args:
        path_config_yaml (Path|str): 追記する config.yaml のパス
        path_pyproject_toml (Path|str): pyproject.toml のパス
    """
    path_yaml = Path(path_config_yaml)
    path_pyproject_toml = Path(path_pyproject_toml)
    etk_version = get_etk_version(path_pyproject_toml)

    # 既存の yaml を読み込む。コメントを保持するために文字列として読み込む。
    with open(path_yaml, encoding='utf-8') as f:
        original_config_str = f.read().strip()

    # yaml に追記する文字列を作成する
    ## ETKのバージョン
    str_etk_version = '\n'.join(
        [
            '# ENUNU Training Kit version',
            f'etk_version: {etk_version}',
        ]
    )
    ## ENUNU拡張機能
    str_enunu_extensions = '\n'.join(
        [
            '# ENUNU extensions',
            'extensions:',
            '    ust_editor:',
            '    timing_editor:',
            '        - "%e/extensions/timing_repairer.py"',
            '        - "%e/extensions/velocity_applier.py"',
            '    acoustic_editor:',
        ]
    )
    # 結合
    new_config_str = '\n\n'.join(
        [
            str_etk_version,
            original_config_str,
            str_enunu_extensions,
        ]
    )
    new_config_str += '\n'  # 最後に改行を追加

    # 既存の yaml に追記する
    with open(path_yaml, 'w', encoding='utf-8') as f:
        f.writelines(new_config_str)
    return new_config_str


if __name__ == '__main__':
    # run_common_steps_devs.sh から呼び出される想定
    args = argv[1:]
    _ = main(
        path_config_yaml=Path(args[0]),
        path_pyproject_toml=Path(args[1]),
    )
    print(f'Edited {args[0]}. ETK version added from {args[1]}.')
