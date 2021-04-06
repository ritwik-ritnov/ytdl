# coding: utf-8
from __future__ import unicode_literals

import datetime
from abc import ABC
from bs4 import BeautifulSoup

from .common import InfoExtractor
from datetime import datetime


class PnsmIE(InfoExtractor, ABC):
    _VALID_URL = r'https?://members\.girlsoutwest\.com/scenes/(?P<id>[a-zA-Z0-9\-=&_]+)'
    _TESTS = [{
        'url': 'https://www.storytel.com/in/en/books/1264920-Panchti-Rahasya-Upanyash---Manavputra',
        'info_dict': {
            'id': '1264920',
            'ext': 'mp3',
            'title': 'Panchti-Rahasya-Upanyash---Manavputra',
        },
        'params': {
            'skip_download': True,
        },
    }]

    _BASE_URL = 'https://members.girlsoutwest.com'


    def _real_extract(self, url):
        display_id = self._match_id(url)

        print(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Authorization': 'Basic TGV6YmlhbjEyMzQ1Omxlc2JpYW5i'
        }
        response = self._download_webpage(url, display_id, headers=headers)

        soup = BeautifulSoup(response, "lxml")

        title = soup.find('div', attrs={'class': 'titleBlock topSpace set_title'}).find('h2').text
        print(title)

        for span_tag in soup.findAll('span'):
            span_tag.replace_with('')
        date_added = soup.find('div', attrs={'class': 'added'}).find('p').text.strip()

        release_year = '0000'
        if(date_added!=''):
            # print(date_added)
            dt = datetime.strptime(date_added, '%m/%d/%Y')
            release_year = dt.year
            print(release_year)

        data = soup.findAll('ul', attrs={'class': 'download_links'})
        formats = []
        for ul in data:
            links = ul.findAll('a')
            for a in links:
                if a['href'] != '#':
                    dl_url = (self._BASE_URL + a['href'])
                    # print(dl_url)
                    formats.append({
                        'url': dl_url,
                        'http_headers': headers,
                        'title': title
                    })
                    break

        return {
            'id': display_id,
            'title': title,
            'formats': formats,
            'release_year': release_year
        }
