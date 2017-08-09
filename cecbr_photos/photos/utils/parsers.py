import attr
import datetime
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
        ps = ParsedSeason(id=unquote(k), name=unquote(album_dict['Name']),
                          date=datetime.strptime(album_dict['AlbumDateAsString'][1:11], '%Y-%m-%d'),
                          count=int(album_dict['PhotoCount']), season=album_dict['SeasonID'],
                          cover_url=unquote(album_dict['CoverPhotoUrl']))
        results.append(ps)
    return results


def get_album(page, album_url):
    parser = FavoriteAlbumParser(page, album_url, array_search_string=ALBUM_TOKEN)
    dicts = parser.parse()
    results = []
    for k, d in dicts:
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
    al_date = attr.ib(validator=attr.validators.instanceof(date))


@attr.s
class ParsedAlbum(object):
    season = attr.ib()
    id = attr.ib()
    small_url = attr.ib()
    large_url = attr.ib()
