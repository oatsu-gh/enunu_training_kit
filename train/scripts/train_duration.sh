if [ -d train/conf/train ]; then
    ext="--config-dir train/conf/train/duration"
else
    ext=""
fi

# if [ ! -z "${pretrained_expdir}" ]; then
#     resume_checkpoint=$pretrained_expdir/${duration_model}/latest.pth
# else
#     resume_checkpoint=
# fi

if [[ ${duration_hydra_optuna_sweeper_args+x} && ! -z $duration_hydra_optuna_sweeper_args ]]; then
    hydra_opt="-m ${duration_hydra_optuna_sweeper_args}"
    post_args="mlflow.enabled=true mlflow.experiment=${expname}_${duration_model} hydra.sweeper.n_trials=${duration_hydra_optuna_sweeper_n_trials}"
else
    hydra_opt=""
    post_args=""
fi

xrun nnsvs-train $ext $hydra_opt \
    model=$duration_model train=$duration_train data=$duration_data \
    +data.in_scaler_path=$dump_norm_dir/in_duration_scaler.joblib \
    +data.out_scaler_path=$dump_norm_dir/out_duration_scaler.joblib \
    data.train_no_dev.in_dir=$dump_norm_dir/$train_set/in_duration/ \
    data.train_no_dev.out_dir=$dump_norm_dir/$train_set/out_duration/ \
    data.dev.in_dir=$dump_norm_dir/$dev_set/in_duration/ \
    data.dev.out_dir=$dump_norm_dir/$dev_set/out_duration/ \
    data.in_scaler_path=$dump_norm_dir/in_duration_scaler.joblib \
    data.out_scaler_path=$dump_norm_dir/out_duration_scaler.joblib \
    train.out_dir=$expdir/duration \
	log_dir=tensorboard/$expname/$duration_model \
	$post_args
    # train.resume.checkpoint=$resume_checkpoint $post_args
