from __future__ import unicode_literals

import base64
import re

from .common import InfoExtractor
from ..compat import compat_urllib_parse_unquote
from ..utils import (
    ExtractorError,
)


class HoichoiBaseIE(InfoExtractor):
    _DOMAINS_REGEX = r'hoichoi\.tv'

    def _get_token(self):
        response = self._download_json(
            'https://prod-api.viewlift.com/identity/anonymous-token?site=hoichoitv', 'token',note='fetching')

        if response is None:
            raise ExtractorError('Unable to get token')

        return response.get('authorizationToken')


class HoichoiIE(HoichoiBaseIE):
    _VALID_URL = r'https?://www\.hoichoi\.tv/(?:fims/title|films/title|videos|films/ttitle)/(?P<id>[^/]+)'

    def _real_extract(self, url):
        display_id = re.match(self._VALID_URL, url).groups()

        webpage = self._download_webpage(url, display_id)

        if ">Sorry, the Film you're looking for is not available.<" in webpage:
            raise ExtractorError(
                'Film %s is not available.' % display_id, expected=True)

        initial_store_state = self._search_regex(
            r"window\.initialStoreState\s*=.*?JSON\.parse\(unescape\(atob\('([^']+)'\)\)\)",
            webpage, 'Initial Store State', default=None)

        film_id = None
        if initial_store_state:
            modules = self._parse_json(compat_urllib_parse_unquote(base64.b64decode(
                initial_store_state).decode()), display_id)['page']['data']['modules']
            content_data = next(m['contentData'][0] for m in modules if m.get('moduleType') == 'VideoDetailModule')
            gist = content_data['gist']
            film_id = gist['id']
            title = gist['title']

        if film_id is None:
            raise ExtractorError('Video Not found')

        token = HoichoiBaseIE._get_token(self)

        headers = {
            'authorization': token
        }

        response = self._download_json(
            'https://prod-api.viewlift.com/content/videos?site=hoichoitv&ids=%s,' % (film_id), film_id,
            headers=headers)

        record = response.get('records')[0]['gist']
        title = record.get('title')
        videoAssets = response.get('records')[0]['streamingInfo'].get('videoAssets')
        formats = []
        for video in videoAssets['mpeg']:
            url = video.get('url')
            renditionValue = video.get('renditionValue')
            bitrate = video.get('bitrate')
            formats.append({
                'url': url,
                'resolution': renditionValue,
                'vbr': bitrate
            })

        return {
            'id': film_id,
            'title': title,
            'formats': formats,
            'ie_key': 'Hoichoi',
        }

class HoichoiShowIE(HoichoiBaseIE):
    _VALID_URL = r'https?://www\.hoichoi\.tv/(?:show|shows)/title/(?P<id>[^/]+)'

    def _real_extract(self, url):
        display_id = re.match(self._VALID_URL, url).groups()
        webpage = self._download_webpage(url, display_id)

        if ">Sorry, the Film you're looking for is not available.<" in webpage:
            raise ExtractorError(
                'Film %s is not available.' % display_id, expected=True)

        initial_store_state = self._search_regex(
            r"window\.initialStoreState\s*=.*?JSON\.parse\(unescape\(atob\('([^']+)'\)\)\)",
            webpage, 'Initial Store State', default=None)

        seasons = None
        if initial_store_state:
            modules = self._parse_json(compat_urllib_parse_unquote(base64.b64decode(
                initial_store_state).decode()), display_id)['page']['data']['modules']
            content_data = next(m['contentData'][0] for m in modules if m.get('moduleType') == 'ShowDetailModule')
            gist = content_data['gist']
            show_id = gist['id']
            p_title = gist['title']
            seasons = content_data['seasons']

        entries = []
        if seasons is not None:
            for season in seasons:
                season_title = season.get('title')
                episodes = season['episodes']
                counter = 1
                for episode in episodes:
                    title = episode.get('title')
                    permalink = episode.get('gist').get('permalink')
                    entry = {
                        '_type': 'url_transparent',
                        'series': p_title,
                        'season': season_title,
                        'episode_number' : counter,
                        'title': title,
                        'url': 'https://www.hoichoi.tv%s'% permalink,
                        'ie_key': HoichoiIE.ie_key(),
                    }
                    entries.append(entry)
                    counter+=1

        return self.playlist_result(entries, display_id, p_title)

class HoichoiShowsRipperIE(HoichoiBaseIE):
    _VALID_URL = r'https?://www\.hoichoi\.tv/(?P<id>[^/]+)'

    def _real_extract(self, url):
        display_id = re.match(self._VALID_URL, url).groups()

        token = HoichoiBaseIE._get_token(self)

        headers = {
            'authorization': token
        }

        response = self._download_json(
            'https://prod-api-cached.viewlift.com/content/pages?path=/%s&languageCode=&includeContent=true&site=hoichoitv'% display_id, display_id, note='fetching...',
            headers=headers)

        if response:
            modules = response['modules']
            content_data = []
            for m in modules:
                if m.get('moduleType') == 'CuratedTrayModule':
                    content_data.append(m['contentData'])

            entries = []
            for content in content_data:
                for data in content:
                    gist = data['gist']
                    show_id = gist['id']
                    show_title = gist['title']
                    perma_link = gist['permalink']
                    isfound = 0
                    for entry_node in entries:
                        if entry_node.get('title') == show_title:
                            isfound = 1
                            break
                    if isfound == 0:
                        if "films" not in perma_link:
                            ie_key = HoichoiShowIE.ie_key()
                        else:
                            ie_key = HoichoiIE.ie_key()
                        entry = {
                            '_type': 'url_transparent',
                            'id': show_id,
                            'title': show_title,
                            'url': 'https://www.hoichoi.tv%s' % perma_link,
                            'ie_key': ie_key,
                            }
                        entries.append(entry)

        return self.playlist_result(entries, show_id, show_id)

