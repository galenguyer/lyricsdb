"""
provides song class
"""
import os
import json
import uuid
from json import JSONEncoder

class Song:
    # pylint: disable=too-few-public-methods
    """
    song class used for json serialization
    """
    def __init__(self, title: str, artist: str, album: str, release: str, lyrics: str, url: str): # pylint: disable=too-many-arguments
        self.title = title
        self.artist = artist
        self.album = album
        self.release = release
        self.lyrics = lyrics
        self.url = url
        self.id = uuid.uuid4().hex

    def obj_creator(d):
        s = Song(d['title'], d['artist'], d['album'], d['release'], d['lyrics'], d['url'])
        s.id = d['id']
        return s

    def get_short_lyrics(self):
        return '\n'.join([line for line in self.lyrics.split('\n')][0:3])

    def save_to_file(self):
        """
        save a song to a file by song name and artist
        """
        if 'genius.com' in self.url:
            filename = './lyrics/genius_'
        elif 'azlyrics.com' in self.url:
            filename = './lyrics/azlyrics_'
        else:
            filename = './lyrics/unknown_'
        for char in self.title.lower():
            if char.isalpha() or char.isdigit():
                filename = filename + char
            if char == ' ':
                filename = filename + '-'
        filename = filename + '_'
        for char in self.artist.lower():
            if char.isalpha() or char.isdigit():
                filename = filename + char
            if char == ' ':
                filename = filename + '-'
        filename = filename + '.json'
        if not os.path.isdir('./lyrics'):
            os.mkdir('./lyrics')
        file = open(filename, 'w')
        json.dump(self, file, indent=4, cls=SongEncoder)
        file.close()


class SongEncoder(JSONEncoder):
    # pylint: disable=too-few-public-methods
    """
    json encoder for song class
    """
    def default(self, o):
        return o.__dict__


if __name__ == '__main__':
    print('this is a module not a standalone app')
