#!/bin/sh

input=$1
IFS=$'\n'
for line in `cat $input`;
do
  echo ${line}
  eval ${line}
done

