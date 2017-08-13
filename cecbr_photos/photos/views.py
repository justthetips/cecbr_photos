from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Season, Album, CampUser, Photo
from .utils import ceimage
import logging

logger = logging.getLogger(__name__)



@login_required()
def album_index(request):
    s = request.session.get('season', '2017')
    season = Season.objects.get(season_name=s)
    cu = CampUser.objects.get(user=request.user)

    albums = Album.objects.filter(season=season)

    new_albums = []
    old_albums = []

    for album in albums:
        if album.processed_date is not None:
            if album.processed_date >= cu.last_album_view:
                new_albums.append(album)
            else:
                old_albums.append(album)

    context = {'new_albums': new_albums, 'old_albums': old_albums, 'season':s}
    return render(request, 'photos/albums_index.html', context)

@login_required()
def album_view(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    logger.debug("Showing Album {}".format(album.name))
    photos = Photo.objects.filter(album=album)

    context = {'album':album, 'photos':photos}
    return render(request, 'photos/album_view.html', context)


@login_required()
def photo_view(request, photo_id):
    photo = get_object_or_404(Photo,id=photo_id)
    cei = ceimage.CEImage(photo)
    context = {'photo':photo, 'cei':cei}
    return render(request, 'photos/photo_view.html', context)
