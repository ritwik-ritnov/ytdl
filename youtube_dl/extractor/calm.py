# coding: utf-8
from __future__ import unicode_literals

from abc import ABC

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    sanitized_Request,
    determine_ext,
)

class CalmIE(InfoExtractor, ABC):
    _VALID_URL = r'https?://app\.www\.calm\.com/player/(?P<id>[^/]+)'
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

    _API_BASE = 'https://api.app.aws-prod.useast1.calm.com'

    def _download_json(self, url_or_request, *args, **kwargs):
        headers = {
            'x-device-platform': 'www',
            'x-is-www-app': 'true'
        }
        for cookie in self._downloader.cookiejar:
            if cookie.name == 'calm-user-token':
                headers['x-session-token'] = cookie.value

        url_or_request = sanitized_Request(url_or_request, headers=headers)

        response = super(CalmIE, self)._download_json(url_or_request, *args, **kwargs)
        self._handle_error(response)
        return response

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            error_str = 'calm.com returned error - %s' % (error.get('code'))
            raise ExtractorError(error_str, expected=True)

    def _real_extract(self, url):
        display_id = self._match_id(url)

        response = self._download_json(
            '%s/programs/guides/%s' % (self._API_BASE, display_id), display_id)

        track_title = response.get('title')

        guide_dict = {}
        for guide in response.get('guides'):
            if guide.get('id') == display_id:
                guide_dict = guide

        formats = []
        if guide_dict.get('video', None) is not None:
            track_url = guide_dict.get('video').get('url')
            track_duration = guide_dict.get('video').get('duration')
            ext = determine_ext(track_url)
            if ext == 'm3u8':
                formats.extend(self._extract_m3u8_formats(
                    track_url, display_id, 'mp4', 'm3u8_native',
                    m3u8_id='hls', fatal=False))
            else:
                formats.append({
                    'format_id': '101',
                    'url': guide_dict.get('video').get('download_url'),
                    'filesize': guide_dict.get('video').get('size'),
                    'ext': ext
                })
        else:
            track_url = guide_dict.get('audio').get('url')
            track_duration = guide_dict.get('audio').get('duration')
            ext = determine_ext(track_url)
            if ext == 'm3u8':
                formats.extend(self._extract_m3u8_formats(
                    track_url, display_id, 'm4a', 'm3u8_native',
                    m3u8_id='hls', fatal=False))
            else:
                formats.append({
                    'format_id': '102',
                    'url': guide_dict.get('audio').get('download_url'),
                    'filesize': guide_dict.get('audio').get('size'),
                    'ext': ext,
                })
        self._sort_formats(formats)

        track_artist = 'None'
        for narrator_it in response.get('narrators'):
            narrator = narrator_it
            track_artist = narrator.get('name')
            break

        track_art_url = ''
        if response.get('background_image') is not None:
            track_art_url = response.get('background_image').get('download_url')

        return {
            'id': display_id,
            'title': track_title,
            'artist': track_artist,
            'thumbnail': track_art_url,
            'duration': track_duration,
            'formats': formats,
        }


class CalmPlayListIE(CalmIE):
    _VALID_URL = r'https?://app\.www\.calm\.com/program/(?P<id>[^/]+)'
    _TESTS = [{
        'url': 'https://app.www.calm.com/program/F4dUIRXP6k',
        'info_dict': {
            'id': 'F4dUIRXP6k',
        },
        'params': {
            'skip_download': True,
        },
    }]

    _API_BASE = 'https://api.app.aws-prod.useast1.calm.com'

    def _download_json(self, url_or_request, *args, **kwargs):
        headers = {
            'x-device-platform': 'www',
            'x-is-www-app': 'true'
        }
        for cookie in self._downloader.cookiejar:
            if cookie.name == 'calm-user-token':
                headers['x-session-token'] = cookie.value

        url_or_request = sanitized_Request(url_or_request, headers=headers)

        response = super(CalmIE, self)._download_json(url_or_request, *args, **kwargs)
        self._handle_error(response)
        return response

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            error_str = 'calm.com returned error - %s' % (error.get('code'))
            raise ExtractorError(error_str, expected=True)

    def _real_extract(self, url):
        display_id = self._match_id(url)

        response = self._download_json(
            '%s/programs/%s' % (self._API_BASE, display_id), display_id)

        playlist_title = response.get('title')

        entries = []
        for guide in response.get('guides'):
            track_id = guide.get('id')
            track_title = guide.get('title')
            entry = {
                '_type': 'url_transparent',
                'url': 'https://app.www.calm.com/player/%s' % track_id,
                'title': track_title,
                'ie_key': CalmIE.ie_key(),
            }
            entries.append(entry)

        return self.playlist_result(entries, display_id, playlist_title)
