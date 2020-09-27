"""
lyric scraper for azlyrics.com
"""

import re

import requests
from bs4 import BeautifulSoup

from .song import Song


class AzSearchResult:
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


def search(term: str) -> [AzSearchResult]:
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
    results = [AzSearchResult(result) for result in search_results]
    return results


def download_url(url: str) -> Song:
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


if __name__ == '__main__':
    print('this is a module not a standalone app')
