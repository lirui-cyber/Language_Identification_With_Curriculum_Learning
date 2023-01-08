#!/usr/bin

save_16k_dir=
data=
. ./utils/parse_options.sh
save_dir=`pwd`/${save_16k_dir}
for x in lre17_train_5_snrs lre17_train_10_snrs lre17_train_15_snrs lre17_train_20_snrs lre17_eval_3s_5_snrs lre17_eval_3s_10_snrs lre17_eval_3s_15_snrs lre17_eval_3s_20_snrs lre17_eval_10s_5_snrs lre17_eval_10s_10_snrs lre17_eval_10s_15_snrs lre17_eval_10s_20_snrs lre17_eval_30s_5_snrs lre17_eval_30s_10_snrs lre17_eval_30s_15_snrs lre17_eval_30s_20_snrs; do
  mkdir ${save_dir}/$x 
  cat ${data}/$x/wav.scp | awk -v n=$x -v p=${save_dir} '{l = length($0); a = substr($0, 0,length-3); print $2" "$3" "$4" "$5" "$6" "$7 " " p "/" n "/" $1 ".wav"}' > ${data}/$x/${x}.cmd
    bash utils/generate_new_wav_cmd.sh ${data}/$x/$x.cmd
done
for x in lre17_eval_3s lre17_eval_10s lre17_eval_30s;do
    for y in 5 10 15 20;do
        cp ${data}/$x/{utt2spk,wav.scp,utt2lang,spk2utt,reco2dur} ${data}/${x}"_"${y}"_snrs/"
        local=${save_dir}"/"${x}"_"${y}"_snrs/"
        cat ${data}/${x}"_"${y}_snrs/wav.scp | awk -v p=$local '{print $1 " " p "noise-" $1 ".wav"}' > ${data}/${x}"_"${y}_snrs/new_wav.scp
        mv ${data}/${x}"_"${y}_snrs/new_wav.scp ${data}/${x}"_"${y}_snrs/wav.scp
    done
done

#for x in lre17_train;do
#    for y in 5 10 15 20;do
#        path=${save_dir}/${x}_${y}_snrs/
#        snrs=_${y}_snrs
#        rm ${data}/${x}_${y}_snrs/{spk2utt,wav.scp}
#        cat ${data}/${x}_${y}_snrs/utt2lang | awk -v p=$path -v s=${snrs} '{l=length($1);name=substr($1,7,l);print name s" " p $1".wav"}' > ${data}/${x}_${y}_snrs/wav.scp
#        cat ${data}/${x}_${y}_snrs/utt2lang | awk -v p=$path -v s=${snrs} '{l=length($1);name=substr($1,7,l);print name s" " $2}' > ${data}/${x}_${y}_snrs/utt2spk
#        cp ${data}/${x}_${y}_snrs/utt2spk ${data}/${x}_${y}_snrs/utt2lang
#        utils/fix_data_dir.sh ${data}/${x}_${y}_snrs/
#    done
#done
