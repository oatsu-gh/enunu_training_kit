# ENUNU Training Kit

USTとLABとＷAVがあれば楽にモデル生成できます。

## 用途

UST ファイルが同梱されている歌唱データベースから、[ENUNU](https://github.com/oatsu-gh/ENUNU) 用の歌声モデルを生成します。

## 必要なもの

- Windows 10

- Python 3.8
- Git for Windows
- Visual C++ v142

## 使い方

1. install.bat をダブルクリックします。（初回のみ）
2. フォルダ "singing_database" に、学習させたい歌唱データベースを丸ごと入れます。音声は **16bit/44.1kHz** にしておくこと。
3. フォルダ "train" を開いて、右クリックメニューの "Git Bash Here" を選択。
4. 表示されている黒い画面に `bash run.sh --stage  0 --stage 6`  と打ち込んでエンターを押します。
5. 待ちます。学習データが多いほど時間がかかります。
6. 処理が正常に終わったら、黒い画面に `python make_it_for_release_enunu.py` と打ち込んでエンターを押します。
7. release フォルダの中に unnamed_--- というフォルダができるので、フォルダ名を変更してください。
8. 名前を変更したフォルダに、readme.txt と character.txt と 空の oto.ini を入れてください。
9. 名前を変更したフォルダを、UTAU の voice フォルダに入れたら完成です。

## 更新履歴

- v0.0.1 (2021-06-13)
  - 学習キット試作
- v0.0.2 (2021-06-14)
  - hedファイルを差し替えて母音無声化に対応
  - enuconfigなどの編集を不要にした
