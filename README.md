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

1. **install_for_cuda111.bat** をダブルクリックします。（初回のみ）
2. フォルダ "singing_database" に、学習させたい歌唱データベースを丸ごと入れます。音声は **16bit/44.1kHz** にしておくこと。
3. フォルダ "train" を開いて、右クリックメニューの "Git Bash Here" を選択。
4. 表示されている黒い画面に `bash run.sh --stage  0 --stop_stage 7`  と打ち込んでエンターを押します。
5. 待ちます。学習データが多いほど時間がかかります。
7. train フォルダの release フォルダの中に unnamed_--- というフォルダができるので、フォルダ名を変更してください。
8. 名前を変更したフォルダに、readme.txt と character.txt と 空の oto.ini を入れてください。
9. 名前を変更したフォルダを、UTAU の voice フォルダに入れたら完成です。

## 更新履歴

- v0.0.1 (2021-06-13)
  - 学習キット試作
- v0.0.2 (2021-06-14)
  - hedファイルを差し替えて母音無声化に対応
  - enuconfigなどの編集を不要にした
- v0.0.3 (2021-06-27)
  - train/conf/prepare_features のフォルダを作成し、myconfig でオーバーライドできるようにした。
  - train/conf/train 以下の各モデルのフォルダに myconfig がないのを修正
- v0.1.0 (2021-06-27)
  - train/conf/prepare_features のフォルダを削除
  - ステージ7としてリリース用フォルダ作成機能を追加
  - ステージ0で無限ル―プすることがある不具合を修正
  - 5ms 未満の音素でエラーが出ないようにする機能を追加
  - どこのステージを実行中か分かりやすくした
- v0.1.1 (2021-07-21)
  - ステージ7が実行されない不具合を修正
  - ステージ0で、LABファイル中の最後の休符の終了時刻を、USTの休符終了時刻に合わせる機能を追加
  - natsort がインストールされない不具合を修正
