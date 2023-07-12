from environment import *
import numpy as np
import tqdm
import os
import subprocess

def XMLconvert(input_file, output_file):
	try:
		print(str(pathenv.MUSESCORE) + " -o " + output_file + " " + input_file)
		#os.system(pathenv.MUSESCORE + " -o " + output_file + " " + input_file)
		subprocess.run([pathenv.MUSESCORE, "-o", output_file, input_file])
	except Exception as inst:
		print("test fail")
		print(inst)