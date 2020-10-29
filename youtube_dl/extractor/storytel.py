# coding: utf-8
from __future__ import unicode_literals

from abc import ABC
import time

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
)


class StorytelIE(InfoExtractor, ABC):
    _VALID_URL = r'https?://www\.storytel\.com/in/en/books/(?P<id>[\d]+)-(?P<name>[a-zA-Z0-9\-]+)'
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

    _API_BASE = 'https://www.storytel.com/nl/nl'
    _TOKEN = 'szMUez5c_8DvNBJksksK4HQeMbkB8392'
    _JWT_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyMDE1MTk1NyIsInNjb3BlIjpbInN0b3J5dGVsOnVzZXIiXSwicmZ0Ijoic3pNVWV6NWNfOER2TkJKa3Nrc0s0SFFlTWJrQjgzOTIiLCJpYXQiOjE1OTg5NzEwNjMsInNleHAiOjE1OTg5NzEzNjMsImV4cCI6MTYwMjQyNzA2MywiaXNzIjoiU1RIUCIsImNpZCI6IjIwMTUxOTU3IiwiZW1haWwiOiJiYUBjYS5jb20iLCJzdG9yZSI6IlNUSFAtSU4iLCJjb3VudHJ5SWQiOiIxNCJ9.HKOgo0RMI1CCV0Rc1QOPhyvni9pnXtq78bAXf2SCDO0'

    def _download_json(self, url_or_request, *args, **kwargs):
        response = super(StorytelIE, self)._download_json(url_or_request, *args, **kwargs)
        self._handle_error(response)
        return response

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            error_str = 'storytel.com returned error - %s' % (error.get('code'))
            raise ExtractorError(error_str, expected=True)

    def _real_extract(self, url):
        display_id = self._match_id(url)

        url = '%s/api/getBookInfoForContent.action?bookId=%s' % (self._API_BASE, display_id)
        print(url)
        response = self._download_json(url,display_id, note = 'getting book info')

        a_id = response.get('slb').get('book').get('AId')
        title = response.get('slb').get('book').get('name')
        author = response.get('slb').get('book').get('authorsAsString')
        duration = response.get('slb').get('abook').get('length')
        composer = response.get('slb').get('abook').get('narratorAsString', "")
        thumb = response.get('slb').get('book').get('largeCover', "")
        release_date = response.get('slb').get('abook').get('releaseDate', "")

        response_headers = ""
        if (a_id is not None):
            # print("sleeping 0 sec")
            # time.sleep(0)
            streamUrl = '%s/mp3streamRangeReq/?startposition=0&token=%s&programId=%s' % (
                self._API_BASE, self._TOKEN, a_id)
            response_headers = super(StorytelIE, self)._request_webpage(streamUrl, a_id, note='getting actual url')

        content_url = response_headers.url

        consume_id = response.get('slb').get('abook').get('consumableFormatId', None)
        chapters = []
        if (consume_id is not None):
            chapters_url = 'https://api.storytel.net/playback-metadata/consumable-format/%s' % consume_id
            headers = {
                'User-Agent': 'Mozilla/5.0 (Android 6.0.1; Mobile; rv:54.0) Gecko/54.0 Firefox/54.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json;charset=utf-8',
                'Authorization': 'Bearer ' + self._JWT_TOKEN,
                'Cache-Control': 'no-cache'
            }
            response = self._download_json(chapters_url, consume_id, note='Getting chapters', headers=headers)
            chapters_json_array = response.get('chapters', [])

            start_time = 0
            counter = 1
            for chapter_dict in chapters_json_array:
                end_time = start_time + chapter_dict.get('durationInSeconds')
                chap_title = chapter_dict.get('title')
                if (chap_title is None):
                    chap_title = counter.__str__()
                chapters.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'title': chap_title,
                })
                start_time = end_time
                counter += 1

        return {
            'id': display_id,
            'title': title,
            'artist': author,
            'album': title,
            'composer': composer,
            'thumbnail': "https://www.storytel.com/" + thumb,
            'ext': 'mp3',
            'duration': duration,
            'chapters': chapters,
            'genre': 'Audiobook',
            'release_date': release_date,
            'url': content_url,
        }


class StorytelAuthorIE(InfoExtractor, ABC):
    _VALID_URL = r'https?://www\.storytel\.com/in/en/authors/(?P<id>[\d]+)-(?P<name>[a-zA-Z0-9\-]+)'
    _TESTS = [{
        'url': 'https://www.storytel.com/in/en/authors/291127-Cupido-And-Others',
        'info_dict': {
            'id': '1264920',
            'ext': 'mp3',
            'title': 'Panchti-Rahasya-Upanyash---Manavputra',
        },
        'params': {
            'skip_download': True,
        },
    }]

    _API_BASE = 'https://www.storytel.in'

    def _download_json(self, url_or_request, *args, **kwargs):
        response = super(StorytelAuthorIE, self)._download_json(url_or_request, *args, **kwargs)
        self._handle_error(response)
        return response

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            error_str = 'storytel.com returned error - %s' % (error.get('code'))
            raise ExtractorError(error_str, expected=True)

    def _get_abooks(self, url, author_id, abooks):

        response = self._download_json(url, author_id, note='Getting books')

        if response.get('books') is None:
            return abooks
        else:
            books = response.get('books')
            for book in books:
                book_obj = book.get('book')
                a_id = book_obj.get('AId')
                bk_id = book_obj.get('id')
                book_name = book_obj.get('name')
                if a_id is not 0:
                    book_dict = {
                        'name': book_name,
                        'id': bk_id
                    }
                    abooks.append(book_dict)

        load_more_url = response.get('loadMoreUrl', '')
        if load_more_url == '':
            return abooks
        else:
            json_url = self._API_BASE + load_more_url
            self._get_abooks(json_url, author_id, abooks)

    def _real_extract(self, url):
        author_id = self._match_id(url)
        author_name = self._match_name(url)

        total_abooks = []
        json_url = '%s/api/getSmartList.action?filterKeys=AUTHOR&filterValues=%s' % (self._API_BASE, author_id)
        self._get_abooks(json_url, author_id, total_abooks)
        print(total_abooks)

        abook_entries = []
        for abook in total_abooks:
            entry = {
                '_type': 'url_transparent',
                'url': "https://www.storytel.com/in/en/books/%d" % abook.get('id') + '-book',
                'title': abook.get('name'),
                'ie_key': StorytelIE.ie_key(),
            }
            abook_entries.append(entry)

        return self.playlist_result(abook_entries, author_id, 'all books')
