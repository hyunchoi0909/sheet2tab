# Script to filter and organize guitar pro tabs from TheGuitarLesson.com
# Removes duplicate songs, and removes extensions that arent gp3, gp4, or gp5
# 
# https://www.theguitarlesson.com/guitar-pro-tabs/database-download/

import sys
import re
import os
import subprocess
from tqdm import tqdm
cwd = os.getcwd()
sys.path.append("..\\sheet2tab")
from environment import *

os.chdir(pathenv.GPTAB_DIR)
initials = os.listdir()
file_extension = {}

# Bool to write all skipped files to log file
output_skip_log = True

# General file stats
total = 0
repeats = 0
wrong_extension = 0
extension_count = {"gp3":0, "gp4":0, "gp5":0}
skip_log = []

# Loop through initial band letter
for initial in tqdm(initials):
    os.chdir(initial)
    bands = os.listdir()

    # Loop through bands
    for band in bands:
        os.chdir(band)
        songs = os.listdir()

        # Loop through songs and check for repeats
        song_dict = {}
        for song in songs:
            total += 1
            extension = song.rsplit(".")[-1]
            
            
            song_title = "".join("".join(song.rsplit("-")[1:]).replace(" ", "").lower().rsplit(".")[:-1])


            pattern = re.compile(r'\(\d+\)')
            check = pattern.search(song_title)

            if check != None:
                skip_log.append(song)
                repeats += 1
                continue

            # skip songs with wrong extension
            if extension in extension_count:
                extension_count[extension] += 1
            else:
                skip_log.append(song)
                wrong_extension += 1
                continue

            # if same song name, choose higher extension
            if song_title in song_dict:
                if extension[-1] >= song_dict[song_title][-1]:
                    skip_log.append(song_dict[song_title])
                    song_dict[song_title] = song
                    extension_count["gp" + song_dict[song_title][-1]] -= 1
                else:
                    skip_log.append(song)
                    extension_count["gp" + extension[-1]] -= 1
                repeats += 1
            else:
                song_dict[song_title] = song

        # copy songs to rawdata directory
        for song in song_dict:
            src = song_dict[song]
            filename = band.replace(" ","").lower() + "-" + song + "." + src.rsplit(".")[-1]
            dst = os.path.join(pathenv.DATA_RAW, filename)
            try:
                subprocess.call(["cp", src, dst])
            except:
                print(" File {} failed with copyint".format(src))
                quit()
        os.chdir("..")
    os.chdir("..")

# Print stats
print("Total Files Processed: " + str(total))
print("Skipped due to repeat: " + str(repeats))
print("Skipped due to wrong_extension: " + str(wrong_extension))

copied = 0
for extension in extension_count:
    copied += extension_count[extension]
processed = repeats + wrong_extension + copied
if processed != total:
    print("WARNING: Total files do not match files processed")
print("Extension Summary:")
for extension in extension_count:
    print("\t" + extension + ":\t" + str(extension_count[extension]))
print("TOTAL FILES COPIED AS DATA: " + str(copied))


# If applicable output log file
if output_skip_log:
    os.chdir(cwd)
    with open("skip_output.txt", "w",encoding="utf-8") as f:
        for skip in skip_log:
            f.write(skip+"\n")
    print("Skipped file output written")