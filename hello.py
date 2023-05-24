import mslib.db_handler.handler
from mslib.recognizer.decoder import *
from mslib.recognizer import fingerprint
from mslib.recognizer import recognizer
import time
from typing import Set
from mslib.config import config
from pprint import pprint

db = mslib.db_handler.handler.MySQLDB()
# db.reset_tables()
recog = recognizer.Recognizer()
recog.fingerprint_directory('./data')
res = recog.recognize_from_microphone()
pprint(res)
# print('---------------')
# res2 = recog.match_song_from_file('./data/Brad-Sucks--Total-Breakdown.mp3', 20)
# pprint(res2)


