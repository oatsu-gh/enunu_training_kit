#!/usr/bin/env python3
# Copyright (c) 2025 oatsu
"""
配布用のzipファイルを作る
"""

from pathlib import Path
import shutil
from tqdm import tqdm
import subprocess
from shutil import make_archive

PYTHON_DIR = 'python-3.12.10-embed-amd64'
PORTABLEGIT_DIR = 'PortableGit-2.52.0'


def pip_uninstall_torch(python_exe: str):
    """
    PyTorchをアンインストールする
    """
    packages = ['torch', 'torchaudio', 'torchvision']
    args = [
        python_exe,
        '-m',
        'pip',
        'uninstall',
        '-y',
    ] + packages
    subprocess.run(args, check=True)  # noqa: S603


def pip_install_upgrade_requirements(python_exe: str, requirements_txt: str):
    """
    pythonのパッケージを更新する
    NOTE: uv を使って高速に実施できると嬉しい。
    """
    #
    args = [
        python_exe,
        '-m',
        'pip',
        'install',
        '--upgrade',
        'setuptools',
        'wheel',
        'uv',
        '--no-warn-script-location',
        '--disable-pip-version-check',
    ]
    subprocess.run(args, check=True)  # noqa: S603

    # requirements.txt に記載されているパッケージを更新
    args = [
        python_exe,
        '-m',
        'uv',
        'pip',
        'install',
        '--upgrade',
        '--no-build-isolation',
        '-r',
        str(requirements_txt),
        '--link-mode=copy',
    ]
    subprocess.run(args, check=True)  # noqa: S603


def remove_cache_files(target_dir: Path):
    """
    キャッシュファイルを削除する。
    """
    # キャッシュフォルダを再帰的に検索
    l_dirs = target_dir.glob('**/__pycache__')
    l_dirs = [path for path in l_dirs if path.is_dir()]
    # キャッシュフォルダを削除
    for cache_dir in tqdm(l_dirs):
        shutil.rmtree(cache_dir)


def copy_python_dir(python_dir: Path, dist_dir: Path):
    """
    配布のほうにPythonをコピーする
    """
    shutil.copytree(python_dir, dist_dir / python_dir.name)


def main(python_dir: Path = Path(PYTHON_DIR)):
    """
    配布用のフォルダを作成する。
    """
    version = input('トレーニングキットのバージョンを入力してください。\n>>> ').lstrip('v')
    assert '.' in version

    script_dir = Path(__file__).resolve().parent
    python_dir = script_dir / python_dir
    dist_dir = script_dir / '_dist' / f'enunu_training_kit-{version}'
    python_exe = python_dir / 'python.exe'
    requirements_txt = script_dir / 'requirements.txt'

    # 配布用フォルダを作成
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)

    # root/python のパッケージを更新
    print('Upgrading packages...')
    pip_install_upgrade_requirements(
        str(python_exe),
        str(requirements_txt),
    )

    # root/python の PyTorchをアンインストール
    print('Uninstalling PyTorch...')
    pip_uninstall_torch(str(python_exe))

    # root/python のキャッシュファイルを削除
    print('Removing cache files...')
    remove_cache_files(python_dir)

    # Pythonをコピー
    print('Copying Python directory...')
    copy_python_dir(python_dir, dist_dir)

    # PortableGitをコピー
    print('Copying PortableGit directory...')
    shutil.copytree(
        script_dir / PORTABLEGIT_DIR,
        dist_dir / PORTABLEGIT_DIR,
    )

    # dist 内に空のフォルダを作る
    print('Creating blank folders...')
    necessary_blank_dirs = ['singing_database']
    for folder in tqdm(necessary_blank_dirs):
        (dist_dir / folder).mkdir()

    # dist 内に必要なフォルダをコピー
    print('Copying necessary folders...')
    necessary_dirs_to_copy = [
        'conf',
        'dic',
        'hed',
        'nnsvs_scripts',
        'pretrained_models',
        'stage0',
        'utils',
    ]
    for dir_name in tqdm(necessary_dirs_to_copy):
        tqdm.write(f'  Copying {dir_name}...')
        shutil.copytree(script_dir / dir_name, dist_dir / dir_name)

    # dist 内に必要なファイルをコピー
    print('Copying necessary files...')
    necessary_files_to_copy = [
        '01_PREPARE.bat',
        '02_TRAIN_ESSENSIAL_MODELS.bat',
        '03_TRAIN_VOCODER_MODEL.bat',
        '04_PACK_MODELS.bat',
        'config.yaml',
        'install_torch_auto.bat',
        'install_torch_cpu.bat',
        'LICENSE.txt',
        'preprocess_data.py',
        'pyproject.toml',
        'README.md',
        'requirements.txt',
        'run.sh',
    ]
    for file_name in tqdm(necessary_files_to_copy):
        tqdm.write(f'  Copying {file_name}...')
        shutil.copy2(script_dir / file_name, dist_dir / file_name)
    # zip圧縮する
    print('Making ZIP archive')
    make_archive(
        dist_dir,
        format='zip',
        root_dir=dist_dir.parent,
        base_dir=dist_dir.name,
    )

    print('Preparation of ETK distribution is complete.')


if __name__ == '__main__':
    main()
