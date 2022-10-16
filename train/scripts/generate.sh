for s in ${testsets[@]}; do
    for typ in timelag duration acoustic; do
        if [ $typ = "timelag" ]; then
            eval_checkpoint=$timelag_eval_checkpoint
            model=timelag
        elif [ $typ = "duration" ]; then
            eval_checkpoint=$duration_eval_checkpoint
            model=duration
        else
            eval_checkpoint=$acoustic_eval_checkpoint
            model=acoustic
        fi

        checkpoint=$expdir/$model/${eval_checkpoint}
        name=$(basename $checkpoint)
        xrun nnsvs-generate model.checkpoint=$checkpoint \
            model.model_yaml=$expdir/$model/model.yaml \
            out_scaler_path=$dump_norm_dir/out_${typ}_scaler.joblib \
            in_dir=$dump_norm_dir/$s/in_${typ}/ \
            out_dir=$expdir/$model/predicted/$s/${name%.*}/
    done
done
