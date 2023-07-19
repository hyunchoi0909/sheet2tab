from .environment import *
import numpy as np
import tqdm
import os
import subprocess
import pandas as pd
import guitarpro

def fileconvert(input_file, file_write = True):
	print("Begin processing: " + input_file)
	tracks = []
	try:
		song = guitarpro.parse(input_file)
		for track in song.tracks:
			# Create dataset
			dataset = {}
			for column in setenv.COLUMNS:
				dataset[column] = []

			# ignore if percussion or wrong form of guitar
			if track.isPercussionTrack: continue
			if len(track.strings) != guitarenv.NUMSTRINGS or track.fretCount != 24: continue
			for i in range(guitarenv.NUMSTRINGS):
				if guitarenv.STRINGS[i] != track.strings[i].value: continue

			# Add notes to dataframe
			beginning = True
			for measure in track.measures:
				for beat in measure.voices[0].beats:
					empty_beat = beat.status == guitarpro.BeatStatus.empty
					rest_beat = beat.status == guitarpro.BeatStatus.rest

					# Skip to first note
					if beginning and (empty_beat or rest_beat):
						continue
					beginning = False
					
					# If tie, just add duration to last note
					#print(beat.status)
					if empty_beat or rest_beat or beat.notes[0].type == guitarpro.NoteType.tie:
						dataset["DURATION"][-1] +=  4.0/beat.duration.value

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