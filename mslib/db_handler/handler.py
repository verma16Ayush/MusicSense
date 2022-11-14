from .connect import my_db
from .query_literals import *


class MySQLDB():

    def __init__(self):
        """
        initialises the DB connection and a cursor to execute queries
        """
        self.cursor = my_db.cursor()
        self.cursor.execute(CREATE_SONGS_TABLE)
        self.cursor.execute(CREATE_FINGERPRINTS_TABLE)
        self.cursor.execute(DELETE_UNFINGERPRINTED)

    def insert_fingerprint(self, fingerprint: str, song_id: int, offset: int):
        """
        inserts a single fingerprint into the db. Had to explicitly typecast
        offset (a numpy.int64) into a python int. wasn't sure where to do it so here it is

        :param fingerprint: the sha1 hash we need to enter the DB
        :param song_id: the song id of the song to wich the hash belongs to
        :param offset: the offset of the anchor peak that was used to generate the hash
        """
        self.cursor.execute(INSERT_FINGERPRINT, (fingerprint, song_id, int(offset)))

    def insert_song(self, song_name: str, file_hash: str, num_hashes: int) -> int:
        '''
        inserts a song into the db

        :param song_name: name of the song file
        :param file_hash: file hash of the song
        :param num_hashes: number of hashes generated for that song
        '''
        self.cursor.execute(INSERT_SONG, (song_name, file_hash, num_hashes))
        return self.cursor.lastrowid

    def clear_db(self):
        """
        clears db and deletes fingerprints and songs tables
        """
        self.cursor.execute(DELETE_ALL_FINGERPRINTS)
        self.cursor.execute(DELETE_ALL_SONGS)
        self.cursor.execute(DROP_FINGERPRINTS)
        self.cursor.execute(DROP_SONGS)

    def delete_unfingerprinted(self):
        """
        deletes fields in songs table which are not fingerprinted
        """
        self.cursor.execute(DELETE_UNFINGERPRINTED)
    
    def reset_tables(self):
        """
        deletes all entries from both songs and fingerprints tables.
        ** USE WITH CAUTION **
        """
        self.cursor.execute(DELETE_ALL_FINGERPRINTS)
        self.cursor.execute(DELETE_ALL_SONGS)


    def __exit__(self):
        self.cursor.close()
        my_db.close()
