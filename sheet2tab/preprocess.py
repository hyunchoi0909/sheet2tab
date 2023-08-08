from .environment import *
import numpy as np
import tqdm
import os
import subprocess
import pandas as pd
import guitarpro as gp
import re
import traceback

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
            rows = {"DUR": [], "PITCHES":[]}
            for i in range(guitarenv.NUMSTRINGS):
                rows["STR{}".format(i)] = []
                rows["TYPE{}".format(i)] = []

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
                        rows["DUR"][-1] = rows["DUR"][-1] + beat.duration.time

                    # If note beat, add row data
                    else:
                        # Set pd dataframe row columns
                        pitches = []
                        dur = beat.duration.time
                        frets = [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
                        notetype = [np.nan]*6
                        # Check if not monophonic
                        if monophonic_flag and len(beat.notes) > 1:
                            monophonic_flag = False

                        # Add note/fret data
                        for note in beat.notes:
                            string = note.string-1
                            if note.type == gp.NoteType.normal:
                                notetype[string] =1
                            elif note.type == gp.NoteType.tie:
                                notetype[string] = 2
                            elif note.type == gp.NoteType.dead:
                                notetype[string] = 3
                            else:
                                continue

                            frets[string] = note.value
                            pitches.append(note.realValue)

                        for i in range(guitarenv.NUMSTRINGS):
                            rows["STR{}".format(i)].append(frets[i])
                            rows["TYPE{}".format(i)].append(notetype[i])
                        rows["DUR"].append(dur)
                        rows["PITCHES"].append(pitches)
            # Concatenate rows into output
            for i in range(guitarenv.NUMSTRINGS):
                rows["STR{}".format(i)] = pd.array(rows["STR{}".format(i)],dtype=pd.Int64Dtype())
                rows["TYPE{}".format(i)] = pd.array(rows["TYPE{}".format(i)],dtype=pd.Int64Dtype())
            output.append((pd.DataFrame(rows), monophonic_flag))
        return output

    except Exception as e:
        print("Error with {}".format(input_file))
        print(e)
        traceback.print_exc()
        return output
        #raise Exception()

def fileconvert(input_file, file_write = True):
    file_prefix = ''.join(re.sub('[^A-Za-z0-9\.\-()]+', '', input_file).rsplit(".")[:-1])
    tracks = process_file(input_file)
    stats = {"num_tracks": 0, "num_mono":0, "num_lines":0}

    for track in tracks:
        file_suffix = "({})".format(stats["num_tracks"])
        df = track[0]
        
        if track[1]:
            
            file_suffix = file_suffix + "mono" 
        if os.path.exists(os.path.join(pathenv.PROCESSED_DATA, file_prefix + file_suffix + ".csv")):
            counter = 1
            while os.path.exists(os.path.join(pathenv.PROCESSED_DATA, file_prefix + file_suffix + "-copy{}".format(counter) + ".csv")):
                counter += 1
            file_suffix = file_suffix + "-copy{}".format(counter)
        
        file_suffix = file_suffix + ".csv"
        if file_write:
            df.to_csv(os.path.join(pathenv.PROCESSED_DATA, file_prefix+file_suffix), header = False, index = False)
            #df.to_csv(os.path.join(pathenv.PROCESSED_DATA, "filetest.csv"), header = False, index = False)

        # If sucessful add to stats
        stats["num_lines"] += df.shape[0]
        if track[1]:
            stats["num_mono"] += 1
        stats["num_tracks"] += 1
    return stats
    #return

def process(files = None, file_write = True):
    os.chdir(pathenv.DATA_RAW)
    output = True
    if files is None:
        files = tqdm.tqdm(os.listdir())
    else:
        output = False
    total_tracks = 0
    total_lines = 0
    total_mono = 0
    files_processed = 0
    errors = []
    for file in files:
        try:
            file_stats = fileconvert(file, file_write)
            total_tracks += file_stats["num_tracks"]
            total_lines += file_stats["num_lines"]
            total_mono += file_stats["num_mono"]
            files_processed += 1
        except:
            errors.append(file)
    if output:
        print("Total files processed: \t{}".format(files_processed))
        print("Total tracks generated: \t{}".format(total_tracks))
        print("Number of monophonic tracks: \t{}".format(total_mono))
        print("Monophonic Percentage: \t {:.2f}%".format(total_mono/float(total_tracks)*100))
        print("Total data entries generated: \t{}".format(total_lines))
        print("Errors: {}".format(len(errors)))
    return total_tracks, total_lines, total_mono, files_processed, errors

def mpi_process(file_write = True):
    from mpi4py import MPI

    os.chdir(pathenv.DATA_RAW)

    comm = comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    files = os.listdir()
    num_files = len(files)
    # ends = [int(rank*(num_files/size)), int((rank+1)*(num_files/size))]
    # if rank == size-1:
    #     ends[1] = num_files
    ends = [int(rank*(num_files/size)), int((rank)*(num_files/size))+100]

    if rank == 0:
        iterator = tqdm.tqdm(files[ends[0]: ends[1]])
    else:
        iterator = files[ends[0]: ends[1]]

    tracks, lines, mono, files_proc, errors = process(iterator, file_write)

    tracks = comm.gather(tracks, root=0)
    lines = comm.gather(lines, root=0)
    mono = comm.gather(mono, root=0)
    files_proc = comm.gather(files_proc, root=0)
    errors = comm.gather(errors, root=0)

    if rank == 0:
        total_tracks = 0
        total_lines = 0
        total_mono = 0
        total_files_processed = 0
        total_errors = 0
        for i in range(size):
            total_tracks += tracks[i]
            total_lines += lines[i]
            total_mono += mono[i]
            total_files_processed += files_proc[i]
            total_errors += len(errors[i])
        print("Total files processed: \t{}".format(total_files_processed))
        print("Total tracks generated: \t{}".format(total_tracks))
        print("Number of monophonic tracks: \t{}".format(total_mono))
        print("Monophonic Percentage: \t {:.2f}%".format(total_mono/float(total_tracks)*100))
        print("Total data entries generated: \t{}".format(total_lines))
        print("Errors: {}".format(total_errors))