"""
lyric scraper for azlyrics.com
"""

import os
import json
import re
from json import JSONEncoder

import requests
from bs4 import BeautifulSoup


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


class SongEncoder(JSONEncoder):
    # pylint: disable=too-few-public-methods
    """
    json encoder for song class
    """
    def default(self, o):
        return o.__dict__


class SearchResult:
    # pylint: disable=too-few-public-methods
    """
    more basic song for selecting from search
    """
    def __init__(self, result):
        self.link = result.a['href']
        self.title = result.a.b.text.strip('" ')
        self.artist = result.find_all('b')[1].text

    def __str__(self):
        return f'{self.title} by {self.artist}'


def search(term: str):
    """
    Search for a term
    """
    original_term = term # pylint: disable=unused-variable
    term = re.sub('[^a-zA-Z0-9 ]+', '', term).strip()
    term = re.sub(' ', '+', term)
    search_page = requests.get(f'https://search.azlyrics.com/search.php?q={term}&w=songs&p=1')
    if search_page.status_code != 200:
        raise Exception(f'Status code {search_page.status_code} for search term ' + \
            '"{original_term}" indicates failure')
    parsed_page = BeautifulSoup(search_page.text, 'html.parser')
    search_results = parsed_page.find_all('td', attrs={'class': 'text-left visitedlyr'})
    results = [SearchResult(result) for result in search_results]
    return results


def download_url(url: str):
    """
    Retrieve the page contents and parse out the lyrics from a given url
    """
    if not url.startswith('https://www.azlyrics.com/lyrics/'):
        raise Exception(f'URL "{url}" does not appear to be a valid azlyrics url')
    result = requests.get(url)
    if result.status_code != 200:
        raise Exception(f'Status code {result.status_code} for url "{url}" indicates failure')
    parsed_page = BeautifulSoup(result.text, 'html.parser')
    # lyrics are consistently on the 20th div in the page
    lyrics = parsed_page.find_all('div', limit=21)[-1].text.strip()
    artist = parsed_page.find_all('b')[0].text.strip().rsplit(' ', 1)[0]
    song_title = parsed_page.find_all('b')[1].text.strip('" ')
    album_info = parsed_page.find_all('div', attrs={'class': 'songinalbum_title'})[0]
    album = album_info.b.text.strip('" ')
    year = album_info.text.rsplit(' ', 1)[1].strip('( )')
    return Song(title=song_title, artist=artist, album=album, release=year, lyrics=lyrics, url=url)


def save_to_file(song: Song):
    """
    save a song to a file by song name and artist
    """
    filename = './lyrics/azlyrics_'
    for char in song.title.lower():
        if char.isalpha() or char.isdigit():
            filename = filename + char
        if char == ' ':
            filename = filename + '-'
    filename = filename + '_'
    for char in song.artist.lower():
        if char.isalpha() or char.isdigit():
            filename = filename + char
        if char == ' ':
            filename = filename + '-'
    filename = filename + '.json'
    if not os.path.isdir('./lyrics'):
        os.mkdir('./lyrics')
    file = open(filename, 'w')
    json.dump(song, file, indent=4, cls=SongEncoder)
    file.close()


if __name__ == '__main__':
    print('this is a module not a standalone app')
