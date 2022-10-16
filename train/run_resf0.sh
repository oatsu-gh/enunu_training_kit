set -e
set -u
set -o pipefail

function xrun () {
    set -x
    $@
    set +x
}

CONFIG_PATH="train/config.yaml"

script_dir=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
NNSVS_COMMON_ROOT="train/scripts"
NNSVS_SHELL_SCRIPTS_ROOT=$NNSVS_COMMON_ROOT
. "$NNSVS_COMMON_ROOT/yaml_parser.sh" || exit 1;

eval $(parse_yaml $CONFIG_PATH "")

train_set="train_no_dev"
dev_set="dev"
eval_set="eval"
datasets=($train_set $dev_set $eval_set)
testsets=($dev_set $eval_set)

dumpdir=target/dump
dump_org_dir="$dumpdir/$spk/org"
dump_norm_dir="$dumpdir/$spk/norm"

stage=0
stop_stage=-1

. $NNSVS_COMMON_ROOT/parse_options.sh || exit 1;


if [ -z ${tag:=} ]; then
    expname="${spk}"
else
    expname="${spk}_${tag}"
fi
expdir="model_exp/$expname"


# Prepare files in singing-database for training
if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
    echo "#########################################"
    echo "#                                       #"
    echo "#  stage 0: Data preparation            #"
    echo "#                                       #"
    echo "#########################################"
    rm -rf $out_dir
    rm -f train/preprocess_data.py.log
    python train/preprocess_data.py $CONFIG_PATH || exit 1;
    echo ""
fi


# Analyze .wav and .lab files
if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 1: Feature generation           #"
    echo "#                                        #"
    echo "##########################################"
    rm -rf $dumpdir
    # changed-----------------------------------------------
    # . $NNSVS_COMMON_ROOT/feature_generation.sh || exit 1;
    # to----------------------------------------------------
    . $NNSVS_SHELL_SCRIPTS_ROOT/feature_generation.sh || exit 1;
    # ------------------------------------------------------
    echo ""
fi


# Train time-lag model
if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 2: Time-lag model training      #"
    echo "#                                        #"
    echo "##########################################"
    # changed-----------------------------------------------
    # . $NNSVS_COMMON_ROOT/train_timelag.sh || exit 1;
    # to----------------------------------------------------
    . $NNSVS_SHELL_SCRIPTS_ROOT/train_timelag.sh || exit 1;
    # ------------------------------------------------------
    echo ""
fi


# Train duration model
if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 3: Duration model training      #"
    echo "#                                        #"
    echo "##########################################"
    # changed-----------------------------------------------
    # . $NNSVS_COMMON_ROOT/train_duration.sh || exit 1;
    # to----------------------------------------------------
    . $NNSVS_SHELL_SCRIPTS_ROOT/train_duration.sh || exit 1;
    # ------------------------------------------------------
    echo ""
fi


# Train acoustic model
if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 4: Training acoustic model      #"
    echo "#                                        #"
    echo "##########################################"
    # changed-----------------------------------------------
    # . $NNSVS_COMMON_ROOT/train_acoustic.sh || exit 1;
    # to----------------------------------------------------
    . $NNSVS_SHELL_SCRIPTS_ROOT/train_acoustic_resf0.sh || exit 1;
    # ------------------------------------------------------
    echo ""
fi


# Generate models from timelag/duration/acoustic models
if [ ${stage} -le 5 ] && [ ${stop_stage} -ge 5 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 5: Feature generation           #"
    echo "#                                        #"
    echo "##########################################"
    # changed-----------------------------------------------
    # . $NNSVS_COMMON_ROOT/generate.sh || exit 1;
    # to----------------------------------------------------
    . $NNSVS_SHELL_SCRIPTS_ROOT/generate.sh || exit 1;
    # ------------------------------------------------------
    echo ""
fi


# Synthesis wav files
if [ ${stage} -le 6 ] && [ ${stop_stage} -ge 6 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 6: Waveform synthesis           #"
    echo "#                                        #"
    echo "##########################################"
    . $NNSVS_COMMON_ROOT/synthesis.sh
    echo ""
fi


# Setup postfilter
if [ ${stage} -le 7 ] && [ ${stop_stage} -ge 7 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 7: Prepare postfilter           #"
    echo "#                                        #"
    echo "##########################################"
    # changed-----------------------------------------------
    # . $NNSVS_COMMON_ROOT/generate.sh || exit 1;
    # to----------------------------------------------------
    . $NNSVS_SHELL_SCRIPTS_ROOT/prepare_postfilter.sh || exit 1;
    # ------------------------------------------------------
    echo ""
fi

# Train mgc postfilter
if [ ${stage} -le 8 ] && [ ${stop_stage} -ge 8 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 8: Training mgc postfilter      #"
    echo "#                                        #"
    echo "##########################################"
    # changed-----------------------------------------------
    # . $NNSVS_COMMON_ROOT/generate.sh || exit 1;
    # to----------------------------------------------------
	postfilter_model="postfilter_mgc"
	postfilter_train="mgc"
	postfilter_data="mgc_data"
    . $NNSVS_SHELL_SCRIPTS_ROOT/train_postfilter.sh || exit 1;
    # ------------------------------------------------------
    echo ""
fi

# Train bap postfilter
if [ ${stage} -le 9 ] && [ ${stop_stage} -ge 9 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 9: Training bap postfilter      #"
    echo "#                                        #"
    echo "##########################################"
    # changed-----------------------------------------------
    # . $NNSVS_COMMON_ROOT/generate.sh || exit 1;
    # to----------------------------------------------------
	postfilter_model="postfilter_bap"
	postfilter_train="bap"
	postfilter_data="bap_data"
    . $NNSVS_SHELL_SCRIPTS_ROOT/train_postfilter.sh || exit 1;
    # ------------------------------------------------------
    echo ""
fi

# Merge postfilter models
if [ ${stage} -le 10 ] && [ ${stop_stage} -ge 10 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 10: Merge postfilter models     #"
    echo "#                                        #"
    echo "##########################################"
    # changed-----------------------------------------------
    # . $NNSVS_COMMON_ROOT/generate.sh || exit 1;
    # to----------------------------------------------------
    python $NNSVS_SHELL_SCRIPTS_ROOT/merge_postfilters.py $expdir/postfilter_mgc/latest.pth $expdir/postfilter_bap/latest.pth $expdir/postfilter || exit 1;
    python $NNSVS_SHELL_SCRIPTS_ROOT/merge_postfilters.py $expdir/postfilter_mgc/best_loss.pth $expdir/postfilter_bap/best_loss.pth $expdir/postfilter || exit 1;
    # ------------------------------------------------------
    echo ""
fi

# Vocoder stuff
#if [ ${stage} -le 11 ] && [ ${stop_stage} -ge 11 ]; then
#    echo "stage 11: Prepare vocoder input/output features"
#    . $NNSVS_COMMON_ROOT/prepare_voc_features.sh
#fi

#if [ ${stage} -le 12 ] && [ ${stop_stage} -ge 12 ]; then
#    echo "stage 12: Compute statistics of vocoder's input features"
#
#    if [[ ${acoustic_features} == *"static_deltadelta_sinevib"* ]]; then
#        ext="--num_windows 3 --vibrato_mode sine"
#    elif [[ ${acoustic_features} == *"static_deltadelta_diffvib"* ]]; then
#        ext="--num_windows 3 --vibrato_mode diff"
#    elif [[ ${acoustic_features} == *"static_only_sinevib"* ]]; then
#        ext="--num_windows 1 --vibrato_mode sine"
#    elif [[ ${acoustic_features} == *"static_only_diffvib"* ]]; then
#        ext="--num_windows 1 --vibrato_mode diff"
#    elif [[ ${acoustic_features} == *"static_deltadelta"* ]]; then
#        ext="--num_windows 3 --vibrato_mode none"
#    elif [[ ${acoustic_features} == *"static_only"* ]]; then
#        ext="--num_windows 1 --vibrato_mode none"
#    else
#        ext=""
#    fi
#
#    xrun python $NNSVS_COMMON_ROOT/scaler_joblib2npy_voc.py \
#        $dump_norm_dir/out_acoustic_scaler.joblib $dump_norm_dir/ \
#        --sample_rate $sample_rate $ext
#fi

#if [ ${stage} -le 13 ] && [ ${stop_stage} -ge 13 ]; then
#    echo "stage 13: Training vocoder using parallel_wavegan"
#    if [ ! -z ${pretrained_vocoder_checkpoint} ]; then
#        extra_args="--resume $pretrained_vocoder_checkpoint"
#    else
#        extra_args=""
#    fi
#    # NOTE: copy normalization stats to expdir for convenience
#    mkdir -p $expdir/$vocoder_model
#    cp -v $dump_norm_dir/in_vocoder*.npy $expdir/$vocoder_model
#    xrun parallel-wavegan-train --config conf/parallel_wavegan/${vocoder_model}.yaml \
#        --train-dumpdir $dump_norm_dir/$train_set/in_vocoder \
#        --dev-dumpdir $dump_norm_dir/$dev_set/in_vocoder/ \
#        --outdir $expdir/$vocoder_model $extra_args
#fi

#if [ ${stage} -le 14 ] && [ ${stop_stage} -ge 14 ]; then
#    echo "stage 14: Synthesis waveforms by parallel_wavegan"
#    if [ -z "${vocoder_eval_checkpoint}" ]; then
#        vocoder_eval_checkpoint="$(ls -dt "${expdir}/${vocoder_model}"/*.pkl | head -1 || true)"
#    fi
#    outdir="${expdir}/$vocoder_model/wav/$(basename "${vocoder_eval_checkpoint}" .pkl)"
#    for s in ${testsets[@]}; do
#        xrun parallel-wavegan-decode --dumpdir $dump_norm_dir/$s/in_vocoder \
#            --checkpoint $vocoder_eval_checkpoint \
#            --outdir $outdir
#    done
#fi

# Copy the models to release directory
if [ ${stage} -le 99 ] && [ ${stop_stage} -ge 99 ]; then
    echo "##########################################"
    echo "#                                        #"
    echo "#  stage 99: Release preparation         #"
    echo "#                                        #"
    echo "##########################################"
    python train/prepare_release.py $CONFIG_PATH || exit 1;
    echo ""
fi
