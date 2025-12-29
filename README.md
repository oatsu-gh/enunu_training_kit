# ENUNU Training Kit

UST と LAB と ＷAV から NNSVS / ENUNU 用モデルを作成するツールです。

## 用途

UST ファイルが同梱されている歌唱データベースから、[ENUNU](https://github.com/oatsu-gh/ENUNU) および [SimpleEnunu](https://github.com/oatsu-gh/SimpleEnunu) 用の歌声モデルを生成します。

## 動作環境

- Windows 10, 11

## 必要なもの

- 歌唱データベース
  - UST
  - LAB
  - WAV

## 使い方

### ボコーダーモデルを作成しない場合

1. フォルダ **singing_database** に、学習させたい歌唱データベースを丸ごと入れます。音声フォーマットは 16bit/44.1kHz または 16bit/48kHz のいずれかに統一しておくこと。
2. **00_Install_torch_auto.bat** をダブルクリックします。(初回のみ)
3. **01_PREPARE.bat** をダブルクリックして待ちます。
4. **02_TRAIN_ESSENSIAL_MODELS.bat** をダブルクリックして待ちます。時間がかかります。
5. **04_PACK_MODELS.bat** をダブルクリックして待ちます。
6. フォルダ packed_models 内に unnamed_etkx.x.x のような名前のフォルダができるので、フォルダ名を変更してください。
7. 名前を変更したフォルダに、readme.txt と character.txt と 空の oto.ini を入れてください。
8. 名前を変更したフォルダを、UTAU の voice フォルダに入れたら完成です。適宜 config.yaml を変更して拡張機能を有効化してください。

### ボコーダーモデルを作成する場合

1. フォルダ singing_database に、学習させたい歌唱データベースを丸ごと入れます。音声フォーマットは **16bit/44.1kHz** または **16bit/48kHz** にしておくこと。
2. **00_Install_torch_auto.bat** をダブルクリックします。(初回のみ)
3. **01_PREPARE.bat** を実行します。
4. **02_TRAIN_ESSENSIAL_MODELS.bat** をダブルクリックして待ちます。時間がかかります。
5. **03_TRAIN_VOCODER_MODEL.bat** をダブルクリックして待ちます。とても時間がかかります。
6. config.yaml の `vocoder_eval_checkpoint` に、上記で訓練した vocoder モデルのフルパスを指定してください。例： `(前略)/exp/unnamed_ETK2.0.0/etk_world_parallel_hn_usfgan_sr48k/checkpoint-50000steps.pkl`
7. **04_PACK_MODELS.bat** をダブルクリックして待ちます。時間がかかります。
8. フォルダ packed_models 内に unnamed_etkx.x.x のような名前のフォルダができるので、フォルダ名を変更してください。
9. 名前を変更したフォルダに、readme.txt と character.txt と 空の oto.ini を入れてください。
10. 名前を変更したフォルダを、UTAU の voice フォルダに入れたら完成です。適宜 config.yaml を変更して拡張機能を有効化してください。


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
- v2.0.0 (2025-12-26)
  - Python を 3.12.10 に更新
  - HN-uSFGAN モデル作成に対応
- v2.0.1 (2025-12-29)
  - 学習時のカレントディレクトリに日本語が含まれるとエラーになるため、警告メッセージを表示する機能を追加
