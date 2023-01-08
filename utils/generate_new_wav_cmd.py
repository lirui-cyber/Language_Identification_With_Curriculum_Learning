#!/usr/bin/env python3
# encoding: utf-8
# write by LiRui, for read model's log to write files for draw curve

import os
import logging
import sys
import subprocess
def generateNewWavFile(wav, segment, path):
  wavFile = open(wav, 'r')
  segFile = open(segment, 'r')

  wavDict = {}
  lines = wavFile.readline()
  while(lines):
    line = lines.split()
    con = ' '.join(line[1:])
    wavDict[line[0]] = con
    lines = wavFile.readline()

  lines = segFile.readline()
  while(lines):
    line = lines.split()
    newName = line[0]
    oldName = line[1]
    start = float(line[2])
    end = float(line[3])
    
    cmd = wavDict[oldName] + " sox -t wav - -t wav -r 16000 " + path + "/" + newName + ".wav trim " + str(start) + " " + str(end - start)
    print(cmd)
    subprocess.call(cmd, shell=True) 
    lines = segFile.readline()
  print("finish!") 


wav = sys.argv[1]
segment  = sys.argv[2]
path = sys.argv[3]
if not os.path.exists(path):
    os.makedirs(path)
generateNewWavFile(wav, segment, path)

