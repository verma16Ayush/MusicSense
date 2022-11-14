import mslib.db_handler.handler
from mslib.recognizer.decoder import *
from mslib.recognizer import fingerprint
import time

db = mslib.db_handler.handler.MySQLDB()
# db.reset_tables()

num_songs = 0
total_hashes_inserted = 0

start_time = time.process_time()
for file in find_files('./data/', ['mp3', '.wav']):
    num_songs += 1
    data = read(file[0])
    if data is not None:
        channels, sample_rate, hash_ = data
        song_name = get_audio_name_from_path(file[0])
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
            db.insert_fingerprint(fp[0], song_id, fp[1])

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