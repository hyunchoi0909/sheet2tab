from .environment import *
import numpy as np
import tqdm
import os
import subprocess
import pandas as pd
import guitarpro as gp

def det_guitar(gp_track):
	if gp_track.isPercussionTrack: return False
	if len(gp_track.strings) != guitarenv.NUMSTRINGS or gp_track.fretCount != 24: return False
	for i in range(guitarenv.NUMSTRINGS):
		if guitarenv.STRINGS[i] != gp_track.strings[i].value: return False
	return True

def process(input_file):
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

					if rest_state:
						rows[-1]["dur"] = rows[-1]["dur"] + beat.duration.time
					else:
						row = {"fret": [[None,None,None,None,None,None]], "type": [[None,None,None,None,None,None]], "pitch": [[]], "dur": [beat.duration.time]}
						for note in beat.notes:

							if note.type == gp.NoteType.normal:
								row["type"][0][note.string-1] = 1
							elif note.type == gp.NoteType.tie:
								row["type"][0][note.string-1] = 2
							elif note.type == gp.NoteType.dead:
								row["type"][0][note.string-1] = 3
							else:
								continue
							row["fret"][0][note.string-1] = note.value
							row["pitch"][0].append(note.realValue)
						row["pitch"][0].sort()
						rows.append(pd.DataFrame(row))
			output.append(pd.concat(rows, ignore_index=True))
		return output

	except Exception as e:
		print("Error with {}".format(input_file))
		print(e)
		return output
		#raise Exception()
'''
def fileconvert(input_file, file_write = True):
	print("Begin processing: " + input_file)
	tracks = []
	try:
		song = gp.parse(input_file)

			# Add notes to dataframe
			
					# Add new beat to dataset
					else:
						pitches = []
						for i in range(guitarenv.NUMSTRINGS):
							dataset["STRING" + str(i)].append(np.nan)
						for note in beat.notes:
							dataset["STRING" + str(note.string-1)][-1] = note.value
							pitches.append(note.realValue)
						dataset["DURATION"].append(4.0/beat.duration.value)
						pitches.sort()
						dataset["PITCH"].append(pitches)

			tracks.append(pd.DataFrame(dataset))
			print(pd.DataFrame(dataset).dtypes)

				
	except Exception as inst:
		print("Test fail with " + input_file)
		print("Error: " + inst)	

	# Write tracks to individual files as csv
	if file_write:
		input_prefix = os.path.splitext(input_file)[0]
		for i, track in enumerate(tracks):
			output_suffix = "(track_{}).csv".format(i)
			print("\tWrite to CSV: " + input_prefix + output_suffix)
			track.to_csv(input_prefix + output_suffix, header = False, index = False)
	print("Processed file " + input_file)

	return tracks
	'''