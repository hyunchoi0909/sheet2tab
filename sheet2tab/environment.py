import os

class pathenv():
	ROOT = __file__
	DATA_RAW = os.path.join(ROOT,"rawdata")
	TRAIN_RAW = os.path.join(DATA_RAW, "train")
	TEST_RAW = os.path.join(DATA_RAW, "test")

class guitarenv():
	NUMSTRINGS = 6
	STRINGS = [64,59,55,50,45,40]