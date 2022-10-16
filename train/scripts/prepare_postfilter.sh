# NOTE: the script is supposed to be used called from nnsvs recipes.
# Please don't try to run the shell script directory.

if [[ -z ${trajectory_smoothing+x} ]]; then
    trajectory_smoothing=false
    trajectory_smoothing_cutoff=50
fi

mkdir -p $expdir/acoustic/norm/
python $NNSVS_SHELL_SCRIPTS_ROOT/extract_static_scaler.py \
    $dump_norm_dir/out_acoustic_scaler.joblib \
    $expdir/acoustic/model.yaml \
    $dump_norm_dir/out_postfilter_scaler.joblib

for s in ${datasets[@]};
do
    if [ ! -e $expdir/acoustic/${acoustic_eval_checkpoint} ]; then
        echo "ERROR: acoustic model checkpoint $expdir/acoustic/${acoustic_eval_checkpoint} does not exist."
        echo "You must train the acoustic model before training a post-filter."
        exit 1
    fi

    # Input
    xrun nnsvs-gen-static-features \
        model.checkpoint=$expdir/acoustic/${acoustic_eval_checkpoint} \
        model.model_yaml=$expdir/acoustic/model.yaml \
        out_scaler_path=$dump_norm_dir/out_acoustic_scaler.joblib \
        in_dir=$dump_norm_dir/$s/in_acoustic/ \
        out_dir=$expdir/acoustic/norm/$s/in_postfilter \
        utt_list=target/data/list/$s.list normalize=true

    if [ -d train/conf/prepare_static_features ]; then
        ext="--config-dir train/conf/prepare_static_features"
    else
        ext=""
    fi

    # Output
    xrun nnsvs-prepare-static-features $ext acoustic=$acoustic_features \
        in_dir=$dump_norm_dir/$s/out_acoustic/ \
        out_dir=$dump_norm_dir/$s/out_postfilter \
        utt_list=target/data/list/$s.list \
		acoustic.sample_rate=$sample_rate \
		acoustic.correct_vuv=$correct_vuv \
		acoustic.relative_f0=$relative_f0
		# acoustic.f0_floor=$f0_floor \
		# acoustic.f0_ceil=$f0_ceil
done


# for convenience
cp -v $dump_norm_dir/out_postfilter_scaler.joblib $expdir/acoustic/norm/in_postfilter_scaler.joblib

# apply normalization for input features
# NOTE: output features are already normalized
# find $expdir/acoustic/org/$train_set/in_postfilter -name "*feats.npy" > train_list.txt
# scaler_path=$expdir/acoustic/norm/in_postfilter_scaler.joblib
# scaler_class="sklearn.preprocessing.StandardScaler"
# xrun nnsvs-fit-scaler list_path=train_list.txt scaler._target_=$scaler_class \
#     out_path=$scaler_path
# rm -f train_list.txt

# for s in ${datasets[@]}; do
#     xrun nnsvs-preprocess-normalize in_dir=$expdir/acoustic/org/$s/in_postfilter \
#         scaler_path=$scaler_path \
#         out_dir=$expdir/acoustic/norm/$s/in_postfilter
# done