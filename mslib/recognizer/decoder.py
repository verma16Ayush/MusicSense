import audioop
import fnmatch
import os
from email.mime import audio
from hashlib import sha1
from typing import Any, List, Tuple

import numpy as np
from pydub import AudioSegment


def find_files(path: str, extensions: List[str]) -> List[Tuple[str, str]]:
    """
    Get all files that meet the specified extensions.

    :param path: path to a directory with audio files.
    :param extensions: file extensions to look for.
    :return: a list of tuples with file name and its extension.
    """
    # Allow both with ".mp3" and without "mp3" to be used for extensions
    extensions = [e.replace(".", "") for e in extensions]

    results = []
    for dirpath, dirname, files in os.walk(path):
        for extension in extensions:
            for f in fnmatch.filter(files, f"*.{extension}"):
                p = os.path.join(dirpath, f)
                results.append((p, extension))
    return results

def unique_hash(file_path: str, block_size: int = 2**20) -> str:
    """ Small function to generate a hash to uniquely generate
    a file. Inspired by MD5 version here:
    http://stackoverflow.com/a/1131255/712997

    Works with large files.

    :param file_path: path to file.
    :param block_size: read block size.
    :return: a hash in an hexagesimal string form.
    """
    s = sha1()
    with open(file_path, "rb") as f:
        while True:
            buf = f.read(block_size)
            if not buf:
                break
            s.update(buf)
    return s.hexdigest().upper()

def read(file_name: str, limit: int | None = None) -> Tuple[List[np.ndarray], int, str] | None:
    # TODO: Add support for 24-bit .wav file
    # TODO: figure out how to type an ndarray

    """
    Reads any file supported by pydub (ffmpeg) and returns the data contained
    within. If file reading fails due to input being a 24-bit wav file,
    exception is raised. 

    Can be optionally limited to a certain amount of seconds from the start
    of the file by specifying the `limit` parameter. This is the amount of
    seconds from the start of the file.

    :param file_name: file to be read.
    :param limit: number of seconds to limit.
    :return: tuple of (list of (channels), sample_rate, content_file_hash).
    """
    try:
        audiofile = AudioSegment.from_file(file_name)

        if limit:
            audiofile = audiofile[:limit * 1000]

        data : np.ndarray = np.fromstring(str(audiofile.raw_data), np.int16, sep='')

        channels  : List[np.ndarray] = []
        for chn in range(audiofile.channels):
            channels.append(data[chn::audiofile.channels])

        audiofile.frame_rate
        return channels, audiofile.frame_rate, unique_hash(file_name) 

    except audioop.error as e:
        print(f'imput file could not be read probably becuase of the file being a 24 bit wav file. The following error was raised {e}')
    
    return None

def get_audio_name_from_path(file_path: str) -> str:
    """
    Extracts song name from a file path.

    :param file_path: path to an audio file.
    :return: file name
    """
    return os.path.splitext(os.path.basename(file_path))[0]
