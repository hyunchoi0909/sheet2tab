from .environment import *
import numpy as np
import tqdm
import os
import subprocess
import pandas as pd
import guitarpro as gp
import re

def det_guitar(gp_track):
    if gp_track.isPercussionTrack: return False
    if len(gp_track.strings) != guitarenv.NUMSTRINGS or gp_track.fretCount != 24: return False
    for i in range(guitarenv.NUMSTRINGS):
        if guitarenv.STRINGS[i] != gp_track.strings[i].value: return False
    return True

# Convert guitarpro file into multiple panda dataframes
def process_file(input_file):
    output = []
    try:
        song = gp.parse(input_file)

        for track in song.tracks:
            # Ignore if not guitar track
            if not det_guitar(track): continue
            monophonic_flag = True
            beginning_flag = True
            rows = []

            for measure in track.measures:
                # Ignore second voice; second voice is usually empty
                for beat in measure.voices[0].beats:
                    rest_state = (beat.status == gp.BeatStatus.rest) or (beat.status == gp.BeatStatus.empty)

                    # Ignore beginning rests
                    if beginning_flag:
                        if rest_state:
                            continue
                        else:
                            beginning_flag = False
                    # If rest beat, add duration to last note
                    if rest_state:
                        rows[-1]["DUR"] = rows[-1]["DUR"] + beat.duration.time

                    # If note beat, add row data
                    else:
                        # Set pd dataframe row columns
                        row = {"PITCH": [[]], "DUR": [beat.duration.time]}
                        for i in range(guitarenv.NUMSTRINGS):
                            row["STR{}".format(i)] = None
                            row["TYPE{}".format(i)] = None

                        # Check if not monophonic
                        if monophonic_flag and len(beat.notes) > 1:
                            monophonic_flag = False

                        # Add note/fret data
                        for note in beat.notes:
                            if note.type == gp.NoteType.normal:
                                row["TYPE{}".format(note.string-1)] = 1
                            elif note.type == gp.NoteType.tie:
                                row["TYPE{}".format(note.string-1)] = 2
                            elif note.type == gp.NoteType.dead:
                                row["TYPE{}".format(note.string-1)] = 3
                            else:
                                continue
                            row["STR{}".format(note.string-1)] = note.value
                            row["PITCH"][0].append(note.realValue)
                        row["PITCH"][0].sort()
                        rows.append(pd.DataFrame(row, columns=setenv.COLUMNS))
            # Concatenate rows into output
            output.append((pd.concat(rows, ignore_index=True), monophonic_flag))
        return output

    except Exception as e:
        print("Error with {}".format(input_file))
        print(e)
        return output
        #raise Exception()

def fileconvert(input_file, file_write = True):
    file_prefix = ''.join(re.sub('[^A-Za-z0-9\.\-()]+', '', input_file).rsplit(".")[:-1])
    tracks = process_file(input_file)
    stats = {"num_tracks": len(tracks), "num_mono":0}
    i = 0
    
    for track in tracks:
        file_suffix = "({})".format(i)
        df = track[0]
        if track[1]:
            stats["num_mono"] += 1
            file_suffix = file_suffix + "mono" 
        if os.path.exists(os.path.join(pathenv.PROCESSED_DATA, file_prefix + file_suffix + ".csv")):
            file_suffix + file_suffix + "-1"
        file_suffix = file_suffix + ".csv"
        if file_write:
            track.to_csv(os.path.join(pathenv.PROCESSED_DATA, file_prefix+file_suffix), header = False, index = False)
        i += 1
    return stats