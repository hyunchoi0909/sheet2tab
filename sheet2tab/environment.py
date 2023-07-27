import os

class pathenv():
	ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
	DATA_RAW = os.path.join(ROOT,"rawdata")
	TRAIN_RAW = os.path.join(DATA_RAW, "train")
	TEST_RAW = os.path.join(DATA_RAW, "test")
	UNUSED_RAW = os.path.join(DATA_RAW, "unused")
	GPTAB_DIR = os.path.join(ROOT,"gptab") 

class setenv():
	#String 0 is highest string
	COLUMNS = ["PITCH","STRING0", "STRING1", "STRING2", "STRING3", "STRING4", "STRING5", "DURATION"]
	COLUMNS_EXTRA = ["MUTE", "HAMMERON", "PULLOFF", "SLIDE"]
class guitarenv():
	NUMSTRINGS = 6
	STRINGS = [64,59,55,50,45,40]