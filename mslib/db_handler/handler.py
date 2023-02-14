from .connect import my_db
from .query_literals import *
from typing import List, Dict, Tuple, Any
from itertools import groupby
from pprint import pprint
import json
class MySQLDB():

    def __init__(self):
        """
        initialises the DB connection and a cursor to execute queries
        """
        self.db = my_db
        self.cursor = my_db.cursor(dictionary=True, buffered=True)
        self.cursor.execute(CREATE_SONGS_TABLE)
        self.cursor.execute(CREATE_FINGERPRINTS_TABLE)
        # self.cursor.execute(DELETE_UNFINGERPRINTED)

    def insert_fingerprint(self, fingerprint: str, song_id: int, offset: int)->int:
        """
        inserts a single fingerprint into the db. Had to explicitly typecast
        offset (a numpy.int64) into a python int. wasn't sure where to do it so here it is

        :param fingerprint: the sha1 hash we need to enter the DB
        :param song_id: the song id of the song to wich the hash belongs to
        :param offset: the offset of the anchor peak that was used to generate the hash
        """
        self.cursor.execute(INSERT_FINGERPRINT, (song_id, fingerprint, int(offset)))
        self.db.commit()
        return self.cursor.lastrowid
        

    def insert_song(self, song_name: str, file_hash: str, num_hashes: int) -> int:
        '''
        inserts a song into the db

        :param song_name: name of the song file
        :param file_hash: file hash of the song
        :param num_hashes: number of hashes generated for that song
        '''
        self.cursor.execute(INSERT_SONG, (song_name, file_hash, num_hashes))
        self.db.commit()
        return self.cursor.lastrowid

    def clear_db(self):
        """
        clears db and deletes fingerprints and songs tables
        """
        self.cursor.execute(DELETE_ALL_FINGERPRINTS)
        self.cursor.execute(DELETE_ALL_SONGS)
        self.cursor.execute(DROP_FINGERPRINTS)
        self.cursor.execute(DROP_SONGS)
        self.db.commit()

    def delete_unfingerprinted(self):
        """
        deletes fields in songs table which are not fingerprinted
        """
        self.cursor.execute(DELETE_UNFINGERPRINTED)
        self.db.commit()
    
    def reset_tables(self):
        """
        deletes all entries from both songs and fingerprints tables.
        ** USE WITH CAUTION **
        """
        self.cursor.execute(DELETE_ALL_FINGERPRINTS)
        self.cursor.execute(DELETE_ALL_SONGS)
        self.db.commit()
    
    def get_songs(self)-> List[Dict[str, str]]:
        self.cursor.execute(SELECT_SONGS)
        songs : List[Dict[str, str]] = self.cursor.fetchall()
        # pprint(songs, indent=2)
        return songs

    def get_song_by_id(self, song_id)->Dict[str, str]:
        self.cursor.execute(SELECT_SONG, (song_id,))
        return self.cursor.fetchone()

    def return_matches(self, hashes: List[Tuple[str, int]],
                       batch_size: int = 1000) -> Tuple[List[Tuple[int, int]], Dict[int, int]]:
        """
        Searches the database for pairs of (hash, offset) values.

        :param hashes: A sequence of tuples in the format (hash, offset)
            - hash: Part of a sha1 hash, in hexadecimal format
            - offset: Offset this hash was created from/at.
        :param batch_size: number of query's batches.
        :return: a list of (sid, offset_difference) tuples and a
        dictionary with the amount of hashes matched (not considering
        duplicated hashes) in each song.
            - song id: Song identifier
            - offset_difference: (database_offset - sampled_offset)
        """
        # Create a dictionary of hash => offset pairs for later lookups
        mapper: Dict[str, List[int]] = {}
        for hsh, offset in hashes:
            if hsh.upper() in mapper.keys():
                mapper[hsh.upper()].append(offset)
            else:
                mapper[hsh.upper()] = [offset]

        values = list(mapper.keys())

        # in order to count each hash only once per db offset we use the dic below
        dedup_hashes: Dict[int, int] = {}

        results = []
        for index in range(0, len(values), batch_size):
            # Create our IN part of the query
            query = SELECT_MULTIPLE % ', '.join([IN_MATCH] * len(values[index: index + batch_size]))

            self.cursor.execute(query, values[index: index + batch_size], )
            cur = self.cursor.fetchall()
            for resitem_dict in cur:
                sid = resitem_dict[FIELD_SONG_ID]
                hsh = resitem_dict[f'HEX(`{FIELD_HASH}`)']
                offset = resitem_dict[FIELD_OFFSET]

                if sid not in dedup_hashes.keys():
                    dedup_hashes[sid] = 1
                else:
                    dedup_hashes[sid] += 1
                #  we now evaluate all offset for each  hash matched
                for song_sampled_offset in mapper[hsh]:
                    results.append((sid, offset - song_sampled_offset))

        return results, dedup_hashes


    def __exit__(self):
        self.cursor.close()
        my_db.commit()
        my_db.close()
