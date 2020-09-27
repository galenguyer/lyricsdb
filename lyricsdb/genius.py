"""
lyric scraper for genius.com
"""

import json
import re

import requests
from bs4 import BeautifulSoup

from .song import Song


class GeniusSearchResult:
    # pylint: disable=too-few-public-methods
    """
    more basic song for selecting from search
    """
    def __init__(self, result):
        result =  result['result']
        self.link = result['url'].encode('ascii', 'ignore').decode('utf-8')
        self.title = result['title'].encode('ascii', 'ignore').decode('utf-8')
        self.artist = result['primary_artist']['name'].encode('ascii', 'ignore').decode('utf-8')

    def __str__(self):
        return f'{self.title} by {self.artist} (via genius)'


def search(term: str) -> [GeniusSearchResult]:
    """
    Search for a term
    """
    original_term = term # pylint: disable=unused-variable
    term = re.sub('[^a-zA-Z0-9 ]+', '', str(term)).strip()
    term = re.sub(' ', '+', str(term))
    search_page = requests.get(f'https://genius.com/api/search/song?page=1&q={term}')
    if search_page.status_code != 200:
        raise Exception(f'Status code {search_page.status_code} for search term ' + \
            '"{original_term}" indicates failure')
    parsed_page = json.loads(search_page.text)
    search_results = parsed_page['response']['sections'][0]['hits']
    results = [GeniusSearchResult(result) for result in search_results]
    return results


def download_url(url: str) -> Song:
    """
    Retrieve the page contents and parse out the lyrics from a given url
    """
    if not url.startswith('https://genius.com/'):
        raise Exception(f'URL "{url}" does not appear to be a valid genius lyrics url')
    result = requests.get(url)
    if result.status_code != 200:
        raise Exception(f'Status code {result.status_code} for url "{url}" indicates failure')
    parsed_page = BeautifulSoup(result.text.replace(u'\u2018', '\'').replace(u'\u2019', '\''),
        'html.parser')
    song_lyrics = parsed_page.find_all('div', attrs={'class': 'lyrics'})[0].text.strip()
    song_data = json.loads([line for line in result.text.split('\n') if 'TRACKING_DATA' in line]\
        [0].split('=')[1].strip(' ;'))
    song_artist = song_data['Primary Artist'].encode('ascii', 'ignore').decode('utf-8')
    song_title = song_data['Title'].encode('ascii', 'ignore').decode('utf-8')
    song_album = (song_data['Primary Album'] if song_data['Primary Album'] is not None \
        else 'Unknown Album').encode('ascii', 'ignore').decode('utf-8')
    song_release = song_data['Release Date'].encode('ascii', 'ignore').decode('utf-8')
    song = Song(title=song_title, artist=song_artist, album=song_album, \
        lyrics=song_lyrics, url=url, release=song_release)
    return song


if __name__ == '__main__':
    print('this is a module not a standalone app')
