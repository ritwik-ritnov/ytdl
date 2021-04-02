# coding: utf-8
from __future__ import unicode_literals

import datetime
from abc import ABC
from bs4 import BeautifulSoup

from .common import InfoExtractor


class XnnmIE(InfoExtractor, ABC):
    _VALID_URL = r'https?://members\.purenudism\.com/members_only/gallery\.cgi\?gid=(?P<id>[a-zA-Z0-9\-_]+)'
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

        url = url.replace('gallery.cgi', 'access/gallery.cgi')
        url = url +'&base_gal_sort=filename&base_gal_thumbs_per_page=125&base_gal_enlarge_size=3'
        print(url)

        headers = {
            'cookie': '__cfduid=d1ef7aa7e390e49dfb69b15229b08653a1615381959; IC=1; USER_DATA=875466193611831808; USER_ID=339661255; PV=4; _ga=GA1.2.1136317412.1615436049',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'authorization': 'Basic dHQzMjE6bm9wYXNzQDEyMw =='
        }
        response = self._download_webpage(url, display_id, headers=headers)

        soup = BeautifulSoup(response, 'lxml')
        tds = soup.findAll('td', attrs={'height': '120'})
        all_links = []
        for tr in tds:
            for a in tr.findAll('a'):
                if a.has_attr('href'):
                    all_links.append(a['href'])

        res = []
        [res.append(x) for x in all_links if x not in res]

        print(res.__len__())
        entries = []
        http_headers = {
            'Referer': 'https://members.purenudism.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        }
        for link in res:
            entry = {
                '_type': 'url_transparent',
                'url': link,
                'http_headers':http_headers
            }
            entries.append(entry)

        title = display_id
        fonts = soup.find_all('font', attrs={'style': 'font-size: 13pt'})
        for font in fonts:
            title = font.text.strip()
            break
        return self.playlist_result(entries, title, title)