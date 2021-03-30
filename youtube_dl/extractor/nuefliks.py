# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    determine_ext,
)
import urllib.parse
from ..utils import (
    determine_ext,
    extract_attributes,
    ExtractorError,
    float_or_none,
    int_or_none,
    js_to_json,
    sanitized_Request,
    try_get,
    unescapeHTML,
    url_or_none,
    urlencode_postdata,
)
import re


class NuefliksEpisodeIE(InfoExtractor):
    _VALID_URL = r'https?://nuefliks\.com/\#/home/episodes/(?P<id>[^/]+)'
    _TESTS = [{
        'url': 'https://nuefliks.com/#/home/episodes/477',
        'info_dict': {
            'id': '477',
            'ext': 'mp4',
            'title': 'Episode 1 of Chithi- Marathi webseries',
        },
        'params': {
            'skip_download': True,
        },
    }]
    _API_BASE = 'https://api.nuefliks.com/'
    JWT_TOKEN = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJqYXkxNTVpbkBnbWFpbC5jb20iLCJleHAiOjE2NDIxMzY2OTcsImRldmljZWlkIjoiamF5MTU1aW5AZ21haWwuY29tVGh1IEphbiAxNCAyMDIxIDEwOjM0OjU4IEdNVCswNTMwIChJbmRpYSBTdGFuZGFyZCBUaW1lKSIsImlhdCI6MTYxMDYwMDY5N30.QmNI17xChapAv4HFBEafYEu1lkawv6ghqYHCGfCwAaOyNwp97QzrjeG7iW1JTvsnB0Kdjhww9oWqy9jGrfSwnQ'

    _HEADERS = {
        'Origin': 'https://nuefliks.com',
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization': JWT_TOKEN,
        'Referer': 'https://api.nuefliks.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'
    }

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            error_str = 'nuefliks returned error - %s' % error
            raise ExtractorError(error_str, expected=True)

    def _real_initialize(self):
        for cookie in self._downloader.cookiejar:
            if cookie.name == 'XSRF-TOKEN':
                self._XSRF_TOKEN = cookie.value

    def _extract_m3u8_formats_h(self, m3u8_url, video_id, ext=None,
                              entry_protocol='m3u8', preference=None,
                              m3u8_id=None, note=None, errnote=None,
                              fatal=True, live=False):
        res = self._download_webpage_handle(
            m3u8_url, video_id,
            note=note or 'Downloading m3u8 information',
            errnote=errnote or 'Failed to download m3u8 information',
            headers=self._HEADERS,
            fatal=fatal)

        if res is False:
            return []

        m3u8_doc, urlh = res
        m3u8_url = urlh.geturl()

        return self._parse_m3u8_formats(
            m3u8_doc, m3u8_url, ext=ext, entry_protocol=entry_protocol,
            preference=preference, m3u8_id=m3u8_id, live=live)

    def _real_extract(self, url):

        groups = re.match(self._VALID_URL, url)
        display_id = groups.group('id')

        detail_response = self._download_json(self._API_BASE + "v1/W/episode/%s" %display_id,display_id, headers=self._HEADERS)
        self._handle_error(detail_response)

        episode_name = detail_response.get('episodeName')

        episode_video_resp = self._download_json(self._API_BASE+ "v1/W/episodelink/%s" %display_id, display_id, headers=self._HEADERS)

        print(episode_video_resp)

        episode_watch_link = episode_video_resp.get('videoLink')

        print(episode_name)
        print(episode_watch_link)

        episode_embed_link = None
        if(episode_watch_link is not None):
            episode_embed_resp = self._download_webpage(episode_watch_link, display_id,
                                                     headers=self._HEADERS)
            episode_embed_link = self._html_search_regex(
                 r'<iframe src=([^ ]+)', episode_embed_resp,
                'iframe path')
            print('link')
            episode_embed_link = episode_embed_link.replace("'", "")
            print(episode_embed_link)

            episode_play_resp = self._download_webpage(episode_embed_link, display_id, headers=self._HEADERS)
            # try:
            #     episode_play_link = self._html_search_regex(
            #     r'<source .*?src=\"(https://www.flizmovies\.(?:org)/[^\"]+)\"\ type=\"application/x-mpegURL\" label=\"AUTO \" res=\"auto\"', episode_play_resp,
            #     'iframe path')
            # except:
            episode_play_link = "https://flizstreams22.akamaized.net/vod/mystery/ep1/smil:play.smil/playlist.m3u8?token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJqYXkxNTVpbkBnbWFpbC5jb20iLCJJUCI6IjI0MDU6MjAxOjgwMGQ6ZjgxNTpiNDBkOmFhOmUyMTM6Yzg5NiIsInN1YnNjcmlwdGlvbiI6MTYxMjYzNjU5MDAwMCwiZXhwIjoxNjEwNjIxNzIwLCJkZXZpY2VpZCI6ImpheTE1NWluQGdtYWlsLmNvbVRodSBKYW4gMTQgMjAyMSAxMDozNDo1OCBHTVQrMDUzMCAoSW5kaWEgU3RhbmRhcmQgVGltZSkiLCJpYXQiOjE2MTA2MTQ1MjB9.6pSWX3F1jG5PfjXdApcYP9BX18EiI7EMNSBx2hDX-83f42q9z--esO_hCkljH-9wEhrT8yOzBHDHRhZP4v1Omw&hdnts=exp=1610614820~acl=*~hmac=ef14268ec3c1e676716ecbb0dd5742f98a3507b8b7d03430340eac2ff1e2b6de"
            print(episode_play_link)

        # secondary_label = video.get('secondary_label')
        # secondary_file = video.get('secondary_file')

        m3u8_formats = self._extract_m3u8_formats_h(
                    episode_play_link, display_id, 'mp4', 'm3u8_native',
                    m3u8_id='hls', fatal=False)

        # formats = []
        # if web_file:
        #     ext = determine_ext(web_file)
        #     if ext == 'm3u8':
        #         m3u8_formats = self._extract_m3u8_formats(
        #             web_file, display_id, 'mp4', 'm3u8_native',
        #             m3u8_id='hls', fatal=False)
        #         for format_info in m3u8_formats:
        #             format_info['language'] = primary_label
        #         formats.extend(m3u8_formats)

        # self._sort_formats(formats)

        return {
            'id': display_id,
            'title': episode_name,
            'formats': m3u8_formats,
        }