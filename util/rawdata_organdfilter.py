import sys
sys.path.append("..\\sheet2tab")
from environment import *

os.chdir(pathenv.GPTAB_DIR)
initials = os.listdir()
file_extension = {}
for initial in initials:
	os.chdir(initial)
	bands = os.listdir()
	for band in bands:
		os.chdir(band)
		songs = os.listdir()
		for song in songs:
			extension = song.rsplit(".")[-1]
			song_title = "".join("".join(song.rsplit("-")[1:]).replace(" ", "").lower().rsplit(".")[:-1])
			print(song_title)
		os.chdir("..")
	os.chdir("..")