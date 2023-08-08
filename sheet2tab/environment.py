import os

class pathenv():
    ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
    DATA_RAW = os.path.join(ROOT,"rawdata")
    CORRUPT_RAW = os.path.join(DATA_RAW, "corrupt")
    PROCESSED_DATA = os.path.join(ROOT, "procdata")
    GPTAB_DIR = os.path.join(ROOT,"gptab")

class setenv():
    #String 0 is highest string, String 5 is the lowest String
    COLUMNS = ["STR0", "STR1", "STR2", "STR3", "STR4", "STR5", "TYPE0", "TYPE1", "TYPE2", "TYPE3", "TYPE4", "TYPE5", "DUR", "PITCH"]
    COLUMNS_EXTRA = ["MUTE", "HAMMERON", "PULLOFF", "SLIDE"]
class guitarenv():
    NUMSTRINGS = 6
    NUMFRETS = 24
    STRINGS = [64,59,55,50,45,40]