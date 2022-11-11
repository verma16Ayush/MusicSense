import mslib.db_handler.handler
from mslib.recognizer.decoder import *
from mslib.recognizer import fingerprint

for file in find_files('./data/', ['mp3', '.wav']):
    data = read(file[0])
    if data is not None:
        channels, sample_rate, hash_ = data
        song_name = get_audio_name_from_path(file[0])
        fingerprint.fingerprint(channel_samples=channels[0], song_name=song_name)
        print(f'''
        file_name: { song_name }
        file_format: {file[1]}
        no_of_channels: {len(channels)}
        sample_rate: {sample_rate},
        no_of_samples: {len(channels[0])}
        file_hash: {hash_}
        -----------------------------------
        ''')