import os
cwd = os.getcwd()
import sys
sys.path.append("..")
from sheet2tab import preprocess
from sheet2tab.environment import *
import pandas as pd
import time
from tqdm import tqdm
import guitarpro as gp
from mpi4py import MPI

os.chdir(pathenv.DATA_RAW)
assert os.path.isdir(pathenv.CORRUPT_RAW)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Determine if track is guitar
def det_guitar(gptrack):
    if track.isPercussionTrack: return False
    if len(track.strings) != guitarenv.NUMSTRINGS or track.fretCount != 24: return False
    for i in range(guitarenv.NUMSTRINGS):
        if guitarenv.STRINGS[i] != track.strings[i].value: return False
    return True

corrupt = []
errors = []

# Split file list by processor
files = os.listdir()
num_files = len(files)
ends = [int(rank*(num_files/size)), int((rank+1)*(num_files/size))]
if rank == size-1:
    ends[1] = num_files

if rank == 0:
    iterator = tqdm(files[ends[0]: ends[1]])
else:
    iterator = files[ends[0]: ends[1]]


for file in iterator:
    if os.path.isdir(file): continue
    try:
        song = gp.parse(file)
        for track in song.tracks:
            check = False
            if not det_guitar(track): continue
            for measure in track.measures:
                if len(measure.voices) > 2:
                    print(file)
                    print(track.name)
                    print(len(measure.voices))
                    check = True
                    break
            if check: break
    except Exception as e:
        song = None
        errors.append("Failure with {}".format(file))
        errors.append(e)
        corrupt.append(file)

corrupt = comm.gather(corrupt, root=0)
if rank==0:
    os.chdir(cwd)
    with open("removed_corruptions.txt","w", encoding="utf-8") as f:
        corrupt_cnt = 0
        for processor in corrupt:
            for file in processor:
                f.write(file)
                f.write("\n")
                corrupt_cnt += 1
        print("# of corrupt files removed: {}".format(corrupt_cnt))

