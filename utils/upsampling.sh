#!/usr/bin

save_16k_dir=

. ./utils/parse_options.sh
for x in lre17_eval_3s lre17_eval_10s lre17_eval_30s;do
    python utils/upsampling_16k.py data/$x/wav.scp ${save_16k_dir}/temp/ ${save_16k_dir}/$x
done
 
