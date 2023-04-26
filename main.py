from fastapi import FastAPI
import mslib.db_handler.handler
from mslib.recognizer.decoder import *
from mslib.recognizer import fingerprint
from mslib.recognizer import recognizer
import time
from typing import Set
from mslib.config import config
from pprint import pprint
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

origins = ['*', 'http://127.0.0.1:3000', 'http://192.168.106.203:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db = mslib.db_handler.handler.MySQLDB()
recog = recognizer.Recognizer()



@app.get("/")
async def root():
    res = recog.recognize_from_microphone()
    return res