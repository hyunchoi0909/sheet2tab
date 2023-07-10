import os

class pathenv():
	ROOT = __file__
	DATA_RAW = os.path.join(ROOT,"rawdata")
	TRAIN_RAW = os.path.join(DATA_RAW, "train")
	TEST_RAW = os.path.join(DATA_RAW, "test")

	MUSESCORE = 'C:\\"Program Files"\\"MuseScore 4"\\bin\\MuseScore4.exe'

class guitarenv():
	test = ""