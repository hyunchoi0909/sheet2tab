import os
cwd = os.getcwd()
import sys
sys.path.append("..")
from sheet2tab import preprocess
from sheet2tab.environment import *
from tqdm import tqdm

corrupt_list_file = "corrupt_list.txt"
f = open(corrupt_list_file)
corrupt_list = f.read().rsplit("\n")
f.close()

#print(corrupt_list)

os.chdir(pathenv.DATA_RAW)
for file in corrupt_list:
    if os.path.isfile(file):
        os.rename(file, os.path.join("corrupt", file))
    else:
        if not os.path.isfile(os.path.join("corrupt", file)):
            print(file)
