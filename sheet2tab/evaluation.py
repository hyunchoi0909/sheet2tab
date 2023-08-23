from .environment import *
import numpy as np
import tqdm
import os
import subprocess
import pandas as pd
import guitarpro as gp
import traceback

class Evaluator():
	def __init__(self, real_data=None, ml_data=None):
		pass

	# Create list of "correct" frettings for a given set of pitches
	## NOTE: fix later to make more easy to read and use less memory; temporary solutoin
	## get rid of invalid ones
	def chord_fretgenerate(self, pitches):
		single_frettings = []
		for pitch in pitches:
			single_frettings.append(self.single_fretgenerate(pitch))
		
		def recurse_fretgenerate(frettings, total_output,correct_fretting = [None]*6, used_strings = [False]*6):
			if len(frettings) == 0:
				total_output.append(correct_fretting)
				return
			for string, fret in enumerate(frettings[0]):
				if fret == None or used_strings[string]:
					continue
				new_correct = correct_fretting.copy()
				new_correct[string] = fret
				new_used = used_strings.copy()
				new_used[string] = True
				recurse_fretgenerate(frettings[1:], total_output, new_correct, new_used) 
				
		correct_frettings = []
		recurse_fretgenerate(single_frettings, correct_frettings)
		return correct_frettings

	# Create a list of correct frettings for a single pitch
	def single_fretgenerate(self, pitch):
		assert type(pitch) == int
		assert pitch <= 88 and pitch >= 40

		correct_frettings = [None, None, None, None, None, None]

		for string, string_pitch in enumerate(guitarenv.STRINGS):
			if pitch < string_pitch: continue
			fretting  = (pitch - string_pitch)
			if fretting <= guitarenv.NUMFRETS:
				correct_frettings[string] = fretting
		return correct_frettings


	def fret_to_pitch(self, string, fret):
		return guitarenv.STRINGS[string] + fret