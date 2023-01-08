#!/bin/bash
#####
# Author:   LiRui
# Date:     Aug 2022
# Project:  ISSAC
# Topic:    Language ID
# Licensed: Nanyang Technological University
#####

echo
echo "$0 $@"
echo

exp=data-16k
dump=source-data/lre17-16k
steps=2

. utils/parse_options.sh || exit 1
. path.sh

steps=$(echo $steps | perl -e '$steps=<STDIN>;  $has_format = 0;
  if($steps =~ m:(\d+)\-$:g){$start = $1; $end = $start + 10; $has_format ++;}
        elsif($steps =~ m:(\d+)\-(\d+):g) { $start = $1; $end = $2; if($start == $end){}elsif($start < $end){ $end = $2 +1;}else{die;} $has_format ++; }  
      if($has_format > 0){$steps=$start;  for($i=$start+1; $i < $end; $i++){$steps .=":$i"; }} print $steps;' 2>/dev/null) || exit 1

if [ ! -z "$steps" ]; then
  for x in $(echo $steps | sed 's/[,:]/ /g'); do
    index=$(printf "%02d" $x)
    declare step$index=1
  done
fi
# Processing data
if [ ! -z $step01 ]; then
  echo -e "____________Step 1: Processing data start @ $(date)____________"
  # Processing training data
  # It is to generate each segment as new 16kHz wavefile, which name is the same as the uttID(1st column) of utt2spk 
  python utils/generate_new_wav_cmd.py data/lre17_train/wav.scp data/lre17_train/segments $dump/lre17_train

  # Processing test data
  # Because the test set does not hava segment, only upsampling is required
  bash utils/upsampling.sh  --save_16k_dir $dump

  # Prepare new kaldi format file 
  bash utils/prepare_new_kaldi_format.sh --save_16k_dir $dump --data $exp

  echo -e "____________Step 1: Processing data ended @ $(date)____________"
fi
# Add Noise
if [ ! -z $step02 ]; then
  echo -e "____________Step 2: Add noise  start @ $(date)____________"
  cd Add-Noise
  bash add-noise-for-lid.sh --steps 2 --src-train ../$exp/lre17_train --noise_dir ../data/rats_noise_channel_BCDFG
  bash add-noise-for-lid.sh --steps 2 --src-train ../$exp/lre17_eval_3s --noise_dir ../data/rats_noise_channel_AEH
  bash add-noise-for-lid.sh --steps 2 --src-train ../$exp/lre17_eval_10s --noise_dir ../data/rats_noise_channel_AEH
  bash add-noise-for-lid.sh --steps 2 --src-train ../$exp/lre17_eval_30s --noise_dir ../data/rats_noise_channel_AEH

  cd ..
  bash utils/generate_wav.sh  --save_16k_dir $dump --data $exp
  echo -e "____________Step 2: Add noise ended @ $(date)____________"
  
fi

