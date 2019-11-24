# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    determine_ext,
)
import re


class AddatimesIE(InfoExtractor):
    _VALID_URL = r'https?://www\.addatimes\.com/show/(?P<slug>[^/]+)/(?P<id>[^/]+)'
    _TESTS = [{
        'url': 'https://www.addatimes.com/show/sufiyana-s2-hindi/Sufiyana-S2-E1',
        'info_dict': {
            'id': '895',
            'ext': 'mp4',
            'title': 'Sufiyana-S2-E1',
        },
        'params': {
            'skip_download': True,
        },
    }]

    _API_BASE = 'https://www.addatimes.com/api'
    _XSRF_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3d3dy5hZGRhdGltZXMuY29tL2FwaS9sb2dpbiIsImlhdCI6MTU3NDU3NjYyOSwiZXhwIjoxNTc0OTM2NjI5LCJuYmYiOjE1NzQ1NzY2MjksImp0aSI6IjdoZGw3TWxaNE5GYmh1UjMiLCJzdWIiOjMzODU5NCwicHJ2IjoiODdlMGFmMWVmOWZkMTU4MTJmZGVjOTcxNTNhMTRlMGIwNDc1NDZhYSIsImRldGFpbHMiOnsiaWQiOjMzODU5NCwiZmlyc3RfbmFtZSI6bnVsbCwibGFzdF9uYW1lIjpudWxsLCJlbWFpbCI6InZpdGVqYWNAbGlueC5lbWFpbCIsInBob25lIjoiIiwicGljdHVyZSI6bnVsbH19.sp1-4CqfQg_5qctoJ2wwnOMT6j1Pv-TF4_h05JGAwcI'

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            error_str = 'addatimes returned error - %s' % error
            raise ExtractorError(error_str, expected=True)

    def _real_initialize(self):
        for cookie in self._downloader.cookiejar:
            if cookie.name == 'XSRF-TOKEN':
                self._XSRF_TOKEN = cookie.value

    def _real_extract(self, url):

        groups = re.match(self._VALID_URL, url)
        display_id = groups.group('id')
        category = groups.group('slug')

        response = self._download_json(
            'https://www.addatimes.com/api/getVideo?video=%s&category=%s&token=%s'
            % (display_id, category, self._XSRF_TOKEN),
            display_id)
        self._handle_error(response)

        video = response.get('video')
        title = video.get('title')
        primary_label = video.get('primary_label')
        web_file = video.get('web_file')
        # secondary_label = video.get('secondary_label')
        # secondary_file = video.get('secondary_file')

        formats = []
        if web_file:
            ext = determine_ext(web_file)
            if ext == 'm3u8':
                m3u8_formats = self._extract_m3u8_formats(
                    web_file, display_id, 'mp4', 'm3u8_native',
                    m3u8_id='hls', fatal=False)
                for format_info in m3u8_formats:
                    format_info['language'] = primary_label
                formats.extend(m3u8_formats)

        # if secondary_file:
        #     ext = determine_ext(secondary_file)
        #     if ext == 'm3u8':
        #         m3u8_formats = self._extract_m3u8_formats(
        #             web_file, display_id, 'mp4', 'm3u8_native',
        #             m3u8_id='hls', fatal=False)
        #         for format_info in m3u8_formats:
        #             format_info['language'] = secondary_label
        #         formats.extend(m3u8_formats)

        self._sort_formats(formats)

        return {
            'id': display_id,
            'title': title,
            'thumbnail': video.get('vertical_image'),
            'formats': formats,
        }

class AddaTimesShowIE(AddatimesIE):
    _VALID_URL = r'https?://www\.addatimes\.com/show/(?P<id>[^/]+)'
    _TESTS = [{
        'url': 'https://www.addatimes.com/show/sufiyana2',
        'info_dict': {
            'id': '770',
        },
        'params': {
            'skip_download': True,
        },
    }]

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            error_str = 'addatimes returned error - %s' % error
            raise ExtractorError(error_str, expected=True)

    def _real_extract(self, url):
        groups = re.match(self._VALID_URL, url)
        display_id = groups.group('id')

        response = self._download_json(
            'https://www.addatimes.com/api/getShow?show_slug=%s'
            % display_id,
            display_id)
        self._handle_error(response)

        playlist_title = response.get('category').get('name')

        entries = []
        for video in response.get('videos'):
            category = video.get('catSlug')
            track_title = video.get('title')
            track_id = video.get('slug')
            entry = {
                '_type': 'url_transparent',
                'url': 'https://www.addatimes.com/show/%s/%s ' % (category, track_id),
                'title': track_title,
                'ie_key': AddatimesIE.ie_key(),
            }
            entries.append(entry)

        return self.playlist_result(entries, display_id, playlist_title)


class AddaTimesRipperIE(AddatimesIE):
    _VALID_URL = r'https?://www\.addatimes\.com/(?P<id>[^/]+)'

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            error_str = 'addatimes returned error - %s' % error
            raise ExtractorError(error_str, expected=True)

    def _real_extract(self, url):
        groups = re.match(self._VALID_URL, url)
        display_id = groups.group('id')

        response = self._download_json(
            'https://www.addatimes.com/api/original/web', display_id)
        self._handle_error(response)

        entries = []
        pages = response.get('data').get('page_sections')
        for page in pages:
            if page['type'] == 3:
                title = page['title']
                slug = page['video_category']['slug']
                if 'furor' not in slug:
                    entry = {
                        '_type': 'url_transparent',
                        'url': 'https://www.addatimes.com/show/%s ' % slug,
                        'title': title,
                        'ie_key': AddaTimesShowIE.ie_key(),
                        }
                    entries.append(entry)

        return self.playlist_result(entries, display_id, display_id)