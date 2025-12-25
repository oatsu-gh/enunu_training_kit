# NOTE: the script is supposed to be used called from nnsvs recipes.
# Please don't try to run the shell script directory.

if [[ -z ${trajectory_smoothing+x} ]]; then
    trajectory_smoothing=false
    trajectory_smoothing_cutoff=50
fi

mkdir -p $expdir/$acoustic_model/norm/
$PYTHON_EXE $NNSVS_COMMON_ROOT/extract_static_scaler.py \
    $dump_norm_dir/out_acoustic_scaler.joblib \
    $expdir/$acoustic_model/model.yaml \
    $dump_norm_dir/out_acoustic_static_scaler.joblib

for s in ${datasets[@]};
do
    if [ ! -e $expdir/$acoustic_model/${acoustic_eval_checkpoint} ]; then
        echo "ERROR: acoustic model checkpoint $expdir/$acoustic_model/${acoustic_eval_checkpoint} does not exist."
        echo "You must train the acoustic model before training a post-filter."
        exit 1
    fi

    # Input
    xrun $PYTHON_EXE -m nnsvs.bin.gen_static_features \
        model.checkpoint=$expdir/$acoustic_model/${acoustic_eval_checkpoint} \
        model.model_yaml=$expdir/$acoustic_model/model.yaml \
        out_scaler_path=$dump_norm_dir/out_acoustic_scaler.joblib \
        in_dir=$dump_norm_dir/$s/in_acoustic/ \
        gt_dir=$dump_norm_dir/$s/out_acoustic/ \
        out_dir=$expdir/$acoustic_model/org/$s/in_postfilter \
        utt_list=data/list/$s.list normalize=false gta=true mgc2sp=true \
        gv_postfilter=true sample_rate=$sample_rate

    if [ -d conf/prepare_static_features ]; then
        ext="--config-dir conf/prepare_static_features"
    else
        ext=""
    fi

    # Output
    # xrun $PYTHON_EXE -m nnsvs.bin.prepare_static_features  $ext acoustic=$acoustic_features \
    #     in_dir=$dump_org_dir/$s/out_acoustic/ \
    #     out_dir=$dump_org_dir/$s/out_postfilter \
    #     utt_list=data/list/$s.list mgc2sp=true sample_rate=$sample_rate
done

# apply normalization for input and output features
# find $dump_org_dir/$train_set/out_postfilter -name "*feats.npy" > train_list.txt
scaler_path=$dump_norm_dir/out_postfilter_scaler.joblib
# scaler_class="sklearn.preprocessing.StandardScaler"
# xrun $PYTHON_EXE nnsvs.bin.fit_scaler list_path=train_list.txt scaler._target_=$scaler_class out_path=$scaler_path
# rm -f train_list.txt

for s in ${datasets[@]}; do
    xrun $PYTHON_EXE -m nnsvs.bin.preprocess_normalize in_dir=$expdir/$acoustic_model/org/$s/in_postfilter \
        scaler_path=$scaler_path \
        out_dir=$expdir/$acoustic_model/norm/$s/in_postfilter
    # xrun $PYTHON_EXE nnsvs.bin.preprocess_normalize in_dir=$dump_org_dir/$s/out_postfilter \
    #     scaler_path=$scaler_path \
    #     out_dir=$dump_norm_dir/$s/out_postfilter
done

# for convenience
cp -v $scaler_path $expdir/$acoustic_model/norm/in_postfilter_scaler.joblib
