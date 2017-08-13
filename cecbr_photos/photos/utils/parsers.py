import datetime
from time import strptime, mktime

import attr

from .web import Page, IndexAlbumParser, unquote, FavoriteAlbumParser

ALBUM_TOKEN = "\\\"SessionIDList\\\":[]}}"


def get_logged_on_page(username, password):
    page = Page(username=username, pwd=password)
    page.log_in()
    return page


def get_season_index(page, season_url):
    parser = IndexAlbumParser(cmp=page, url=season_url)
    dicts = parser.parse()
    results = []
    for k, album_dict in dicts.items():
        l_id = unquote(k)
        l_name = unquote(album_dict['Name'])
        l_date = mktime(strptime(album_dict['AlbumDateAsString'][1:11], '%Y-%m-%d'))
        l_count = int(album_dict['PhotoCount'])
        l_season = album_dict['SeasonID']
        l_url = unquote(album_dict['CoverPhotoUrl'])
        ps = ParsedSeason(id=l_id, name=l_name, al_date=datetime.datetime.fromtimestamp(l_date),
                          count=l_count, season=l_season, cover_url=l_url)
        results.append(ps)
    return results


def get_album(page, album_url):
    parser = FavoriteAlbumParser(page, album_url, array_search_string=ALBUM_TOKEN)
    dicts = parser.parse()
    results = []
    for k, d in dicts.items():
        pa = ParsedAlbum(id=unquote(k), season=unquote(d['SeasonID']),
                         small_url=unquote(d['ThumbnailUrl']), large_url=unquote(d['ZoominUrl']))
        results.append(pa)
    return results


@attr.s
class ParsedSeason(object):
    season = attr.ib()
    id = attr.ib()
    name = attr.ib()
    cover_url = attr.ib()
    count = attr.ib(convert=int)
    al_date = attr.ib(validator=attr.validators.instance_of(datetime.date))


@attr.s
class ParsedAlbum(object):
    season = attr.ib()
    id = attr.ib()
    small_url = attr.ib()
    large_url = attr.ib()
