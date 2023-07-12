from .environment import *
import numpy as np
import tqdm
import os
import subprocess
import guitarpro

def fileconvert(input_file):
	tracks = []
	try:
		song = guitarpro.parse(input_file)
		for track in song.tracks:
			dataset = []
			if track.isPercussionTrack: continue
			if len(track.strings) != guitarenv.NUMSTRINGS or track.fretCount != 24: continue
			for i in range(guitarenv.NUMSTRINGS):
				if guitarenv.STRINGS[i] != track.strings[i].value: continue

			for measure in track.measures:
				for beat in measure.voices[0].beats:
					datapoint = [4.0/beat.duration.value,[-1]*guitarenv.NUMSTRINGS]
					for note in beat.notes:
						datapoint[1][note.string-1] = note.value
					dataset.append(datapoint)
			tracks.append(dataset)
	except Exception as inst:
		print("test fail with " + input_file)
		print(inst)
	return tracks