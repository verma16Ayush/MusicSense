import mslib.db_handler.handler
from mslib.recognizer.decoder import *
from mslib.recognizer import fingerprint
import time
from itertools import groupby
import numpy as np
import pyaudio
from typing import Set, Dict, Any
from mslib.config.config import *
from pprint import pprint

class Recognizer():
    default_chunksize = 8192
    default_format = pyaudio.paInt16
    default_channels = 2
    default_samplerate = 44100

    def __init__(self):
        # create a db connection
        self.db = mslib.db_handler.handler.MySQLDB()
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.data = []
        self.channels = Recognizer.default_channels
        self.chunksize = Recognizer.default_chunksize
        self.samplerate = Recognizer.default_samplerate
        self.recorded = False

    def fingerprint_directory(self, path: str, reset_tables:bool = False):
        '''
        learn a song from a given directory of files. finds all supported audio files
        present in the directory. fingerprints them and updates db. skips files that have already been fingerprinted

        '''
        if reset_tables:
            self.db.reset_tables()
        fingerprinted_song_hash_set: Set[str] = set()
        songs_in_db = self.db.get_songs();

        for song in songs_in_db:
            song_hash = song[FIELD_FILE_SHA1]
            fingerprinted_song_hash_set.add(song_hash)

        num_songs = 0
        total_hashes_inserted = 0

        start_time = time.process_time()
        for file in find_files(path, ['mp3', '.wav']):
            num_songs += 1
            data = read(file[0])
            if data is not None:
                channels, sample_rate, hash_ = data
                song_name = get_audio_name_from_path(file[0])

                if hash_ in fingerprinted_song_hash_set:
                    print(f'file: {song_name} already fingerprinted. continuing...')
                    continue

                fingerprints = fingerprint.fingerprint(channel_samples=channels[0], song_name=song_name)

                print(f'''
                ******** processing file ***********
                file_name: { song_name }
                file_format: {file[1]}
                no_of_channels: {len(channels)}
                sample_rate: {sample_rate},
                no_of_samples: {len(channels[0])}
                file_hash: {hash_}
                num_hashes: {len(fingerprints)}
                -----------------------------------
                ''')

                song_id = self.db.insert_song(song_name, hash_, len(fingerprints))

                for fp in fingerprints:
                    rowid = self.db.insert_fingerprint(fp[0], song_id, fp[1])

                total_hashes_inserted += len(fingerprints)

        time_taken = time.process_time() - start_time

        print(f'''
        *********************************************************
        *                      SUMMARY                          *
        *********************************************************

        * total songs processed: {num_songs}
        * total fingerprints inserted: {total_hashes_inserted}
        * time taken: {time_taken}

        *********************************************************
        ''')
        return

    def align_matches(self, matches: List[Tuple[int, int]], dedup_hashes: Dict[int, int], queried_hashes: int,
                      topn: int = TOPN) -> List[Dict[str, Any]]:
        """
        Finds hash matches that align in time with other matches and finds
        consensus about which hashes are "true" signal from the audio.

        :param matches: matches from the database
        :param dedup_hashes: dictionary containing the hashes matched without duplicates for each song
        (key is the song id).
        :param queried_hashes: amount of hashes sent for matching against the db
        :param topn: number of results being returned back.
        :return: a list of dictionaries (based on topn) with match information.
        """
        # count offset occurrences per song and keep only the maximum ones.
        sorted_matches = sorted(matches, key=lambda m: (m[0], m[1]))
        counts = [(*key, len(list(group))) for key, group in groupby(sorted_matches, key=lambda m: (m[0], m[1]))]
        songs_matches = sorted(
            [max(list(group), key=lambda g: g[2]) for key, group in groupby(counts, key=lambda count: count[0])],
            key=lambda count: count[2], reverse=True
        )

        songs_result = []
        for song_id, offset, _ in songs_matches[0:topn]:  # consider topn elements in the result
            song = self.db.get_song_by_id(song_id)
            song_name = song.get(SONG_NAME, None)
            song_hashes = song.get(FIELD_TOTAL_HASHES, 1)
            nseconds = round(float(offset) / DEFAULT_FS * DEFAULT_WINDOW_SIZE * DEFAULT_OVERLAP_RATIO, 5)
            hashes_matched = dedup_hashes[song_id]

            song = {
                SONG_ID: str(song_id),
                SONG_NAME: str(song_name),
                INPUT_HASHES: str(queried_hashes),
                FINGERPRINTED_HASHES: str(song_hashes),
                HASHES_MATCHED: str(hashes_matched),
                # Percentage regarding hashes matched vs hashes from the input.
                INPUT_CONFIDENCE: str(round(hashes_matched / queried_hashes, 2)),
                # Percentage regarding hashes matched vs hashes fingerprinted in the db.
                FINGERPRINTED_CONFIDENCE: str(round(hashes_matched / int(song_hashes), 2)),
                OFFSET: str(offset),
                OFFSET_SECS: str(nseconds),
                FIELD_FILE_SHA1: str(song.get(FIELD_FILE_SHA1, None))
            }

            songs_result.append(song)

        return songs_result

    def match_song_from_file(self, path: str, start_time: int = 0, duration: int = 5) -> List[Dict[str, Any]]:
        '''
        given a path to a file. match a song read from the db. 
        :param path: full path to the file to be matched
        :param start_time: start time on the audio file in seconds. defaults to start of the file
        :param duration: duration from the start time. defaults to 5 seconds
        :return: A list of dictionary with relevant matched information
        '''
        data = read(path)

        if data is not None:
            channels, fs, hash_ = data
            fingerprints = fingerprint.fingerprint(channel_samples=channels[0][start_time * fs : min((start_time + duration) * fs, len(channels[0]))])
            results, dedup_hashes = self.db.return_matches(hashes=fingerprints)

            if results is not None and dedup_hashes is not None:
                matches = self.align_matches(results, dedup_hashes, len(fingerprints))
                return matches
        return []

    def start_recording(self, channels=default_channels,
                        samplerate=default_samplerate,
                        chunksize=default_chunksize):
        print("* start recording")
        self.chunksize = chunksize
        self.channels = channels
        self.recorded = False
        self.samplerate = samplerate

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.stream = self.audio.open(
            format=self.default_format,
            channels=channels,
            rate=samplerate,
            input=True,
            frames_per_buffer=chunksize,
        )

        self.data = [[] for i in range(channels)]
    
    def process_recording(self):
        print("* recording")
        data = self.stream.read(self.chunksize)
        nums = np.fromstring(data, np.int16)
        # print(nums)
        for c in range(self.channels):
            self.data[c].extend(nums[c::self.channels])

    def stop_recording(self):
        print("* done recording")
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.recorded = True

    def recognize_from_microphone(self, duration: int = 10)->List[Dict[str, Any]]:
        self.start_recording()
        for i in range(0, int(self.samplerate / self.chunksize * int(duration))):
            self.process_recording()
        self.stop_recording()

        if not self.recorded:
            raise Exception()
        
        hashes: Set[Tuple[str, int]] = set()

        for channel in self.data:
            fingerprints = fingerprint.fingerprint(channel_samples=channel)
            hashes |= set(fingerprints)
        
        matches, dedup_hashes = self.db.return_matches(fingerprints)

        final_results = self.align_matches(matches=matches, dedup_hashes=dedup_hashes, queried_hashes=len(fingerprints))
        return final_results