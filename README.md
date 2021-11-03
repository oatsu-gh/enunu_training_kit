# ENUNU Training Kit

USTとLABとＷAVがあれば楽にモデル生成できます。

## 用途

UST ファイルが同梱されている歌唱データベースから、[ENUNU](https://github.com/oatsu-gh/ENUNU) 用の歌声モデルを生成します。

## 動作環境

- Windows 10

## 必要なもの

- 歌唱データベース
  - UST
  - LAB
  - WAV

## 使い方

1. フォルダ "train" を開きます。
2. **install_pytorch_for_CPU.bat** をダブルクリックします。CUDA 環境がある場合は、代わりに **install_pytorch_for_CUDA102.bat** または **install_pytorch_for_CUDA113.bat** をダブルクリックします。 (初回のみ)
3. フォルダ "singing_database" に、学習させたい歌唱データベースを丸ごと入れます。音声は **16bit/44.1kHz** にしておくこと。
4. run.bat または run_rmdn.bat をダブルクリックします。
5. 待ちます。学習データが多いほど時間がかかります。 (波音リツDBを使うと、i7-7700 + GTX1070 で実行した場合、通常モデルは1時間くらい、RMDNのほうは10時間くらいかかります。)
6. release フォルダの中に unnamed_--- というフォルダができるので、フォルダ名を変更してください。
7. 名前を変更したフォルダに、readme.txt と character.txt と 空の oto.ini を入れてください。
8. 名前を変更したフォルダを、UTAU の voice フォルダに入れたら完成です。

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
- v0.2.0 (2021-09-17)
  - DBチェック機能を強化（[ENUNU/train](https://github.com/oatsu-gh/ENUNU/tree/main/train) から複製）
- v1.0.0 (2021-11-03)
  - Python Embeddable + Portable Git をポータブル環境にした。（[ENUNU/train](https://github.com/oatsu-gh/ENUNU/tree/main/train) から複製）
  - LICENSE を GPL 2 に変更
