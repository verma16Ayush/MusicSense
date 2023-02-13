import mslib.db_handler.handler
from mslib.recognizer.decoder import *
from mslib.recognizer import fingerprint
import time
from typing import Set
from mslib.config import config
db = mslib.db_handler.handler.MySQLDB()
# db.reset_tables()

def learn_songs_from_directory(path: str, reset_tables:bool = False):
    if reset_tables:
        db.reset_tables()
    fingerprinted_song_hash_set: Set[str] = set()
    songs_in_db = db.get_songs();

    for song in songs_in_db:
        song_hash = song[config.FIELD_FILE_SHA1]
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

            song_id = db.insert_song(song_name, hash_, len(fingerprints))

            for fp in fingerprints:
                rowid = db.insert_fingerprint(fp[0], song_id, fp[1])
                # print(fp)

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

def try_to_match_a_song_from_file(path: str):
    data = read(path)
    if data is not None:
        channels, fs, hash_ = data
        fingerprints = fingerprint.fingerprint(channel_samples=channels[0][3*fs: 50*fs])
        results, dedup_hashes = db.return_matches(hashes=fingerprints)

        if results is not None and dedup_hashes is not None:
        #     for result in results:
        #         print(result)
            
            print(dedup_hashes)

    pass


learn_songs_from_directory('./data/')
try_to_match_a_song_from_file(path='./data/retro-city.mp3')

# db.get_songs()
