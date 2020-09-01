# coding: utf-8
from __future__ import unicode_literals

from abc import ABC

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    sanitized_Request,
    determine_ext,
)

class EnvisionIE(InfoExtractor, ABC):
    _VALID_URL = r'https?://envisionmeditation\.com/'
    _TESTS = [{
        'url': 'https://app.www.calm.com/player/nNpBWr7A9',
        'info_dict': {
            'id': 'BVLV98v',
            'ext': 'm4a',
            'title': 'Blue Gold',
        },
        'params': {
            'skip_download': True,
        },
    }]

    _API_URL = 'https://envision.app/api_v4/get_packs'
    _FILE_BASE= 'https://envision.app/'

    def _download_json(self, url_or_request, *args, **kwargs):
        url_or_request = sanitized_Request(url_or_request)

        response = super(EnvisionIE, self)._download_json(url_or_request, *args, **kwargs)
        self._handle_error(response)
        return response

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            error_str = 'env.com returned error - %s' % (error.get('code'))
            raise ExtractorError(error_str, expected=True)

    def _real_extract(self, url):
        # display_id = self._match_id(url)

        response = self._download_json(self._API_URL, '101')

        entries = []
        data = response.get('data')
        for pack in data:
            pack_title = pack.get('name')
            thumb = None
            if pack.get('image') is not None:
                thumb = self._FILE_BASE + pack.get('image')
            sessions = pack.get('sessions')

            counter = 1
            for session in sessions:
                track_title = session.get('name')
                file_ep = session.get('file')
                if file_ep != '':
                    file_url = self._FILE_BASE  + session.get('file')
                    track_num = counter.__str__() + '/' +len(sessions).__str__()
                    entry = {
                        '_type': 'url_transparent',
                        'url': file_url,
                        'thumbnail': thumb,
                        'album': pack_title,
                        'track_number': track_num,
                        'title': track_title,
                        'artist': 'EnVision'
                    }
                    entries.append(entry)
                    counter+=1

        return self.playlist_result(entries, '101', 'EnVision - Daily Visualization [2020]')
