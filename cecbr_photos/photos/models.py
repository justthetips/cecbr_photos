from django.db import models
import django.utils.timezone
from cecbr_photos.users.models import User
from .utils import parsers
from .utils import web
import logging
import json

import cv2
from PIL import Image
import requests
from io import BytesIO
from django.conf import settings
import numpy as np


import cecbr_photos.photos.utils.FaceDetector
import cecbr_photos.photos.utils.openface
import cecbr_photos.photos.utils.aligndlib
import cecbr_photos.photos.utils.ImageUtils

logger = logging.getLogger(__name__)


def photo_directory_path_s(instance, filename):
    return 'season_{0}/album_{1}/small/{2}'.format(instance.album.season, instance.album.id, filename)


def photo_directory_path_l(instance, filename):
    return 'season_{0}/album_{1}/full/{2}'.format(instance.album.season, instance.album.id, filename)


def training_directory_path(instance, filename):
    return 'person_{0}/{1}'.format(instance.person.name, filename)


class CampUser(models.Model):
    user = models.OneToOneField(User)
    cecbr_uname = models.CharField(max_length=128,
                                   null=False,
                                   verbose_name=u"CECBR User Name",
                                   help_text=u"Please enter your CECBR User Name...")
    cecbr_pwd = models.CharField(max_length=128,
                                 null=False,
                                 verbose_name=u"CECBR Password",
                                 help_text=u"Please enter your CECBR Password...")
    last_album_view = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return self.user.name

    class Meta:
        verbose_name = "Camp User"
        verbose_name_plural = "Camp Users"


class Season(models.Model):
    season_name = models.CharField(max_length=4, null=False, verbose_name=u'Season Name')

    def season_url(self, base_url):
        season_param = '='.join(['seasonID', self.season_name])
        full_url = '?'.join([base_url, season_param])
        return full_url

    def process_season(self, camp_user):
        logger.info("Processing Season {}".format(self.season_name))
        logon_page = parsers.get_logged_on_page(camp_user.cecbr_uname, camp_user.cecbr_pwd)
        albums = parsers.get_season_index(logon_page, self.season_url(web.SEASON_URL))
        for a in albums:
            if Album.objects.filter(id=a.id).exists():
                logger.debug("Album {} exists, checking to see if photo count changed".format(a.name))
                old_album = Album.ojects.get(id=a.id)
                if old_album.count != a.count:
                    logger.info("Album {}'s photo count changed, it went from {} to {}".format(a.name, old_album.count,
                                                                                               a.count))
                    old_album.count = a.count
                    old_album.processed = False
                    old_album.analyzed = False
                    old_album.processed_date = None
                    old_album.analyzed_date = None
                    old_album.save()
            else:
                logger.info("Adding new album {}".format(a.name))
                new_album = Album(season=self, id=a.id, name=a.name, cover_url=a.cover_url, count=a.count,
                                  date=a.al_date)
                new_album.save()

    def _get_album_count(self):
        return Album.objects.filter(season=self).count()

    album_count = property(_get_album_count)

    def __str__(self):
        return self.season_name

    class Meta:
        verbose_name = "Season"
        verbose_name_plural = "Seasons"


class Album(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, blank=False)
    cover_url = models.URLField(blank=False)
    count = models.IntegerField(blank=False)
    date = models.DateField(blank=False)
    processed = models.BooleanField(default=False)
    analyzed = models.BooleanField(default=False)
    processed_date = models.DateTimeField(blank=True, null=True)
    analyzed_date = models.DateTimeField(blank=True, null=True)

    def album_url(self, base_url):
        season_param = '='.join(['seasonID', self.season.season_name])
        album_param = '='.join(['albumID', str(self.id)])
        full_url = '?'.join([base_url, '&'.join([season_param, album_param])])
        return full_url

    def process_album(self, camp_user):
        logger.info("Processing Album {} it has {} photos".format(self.name, self.count))
        logon_page = parsers.get_logged_on_page(camp_user.cecbr_uname, camp_user.cecbr_pwd)
        photos = parsers.get_album(logon_page, self.album_url(web.ALBUM_URL))
        for p in photos:
            if not Photo.objects.filter(id=p.id).exists():
                logger.debug('Photo {} is new, adding it'.format(p.id))
                photo = Photo(album=self, id=p.id, small_url=p.small_url, large_url=p.large_url)
                photo.save()
        self.processed = True
        self.processed_date = django.utils.timezone.now()
        self.save()

    class Meta:
        ordering = ['season', '-date']
        verbose_name = 'Album'
        verbose_name_plural = 'Albums'


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    small_url = models.URLField(blank=False)
    large_url = models.URLField(blank=False)
    small_image = models.ImageField(upload_to='photo_directory_path_s', null=True, blank=True,
                                    verbose_name=u'Small Image')
    large_image = models.ImageField(upload_to='photo_directory_path_l', null=True, blank=True,
                                    verbose_name=u'Large Image')
    json_data = models.TextField(blank=True, null=True)
    analyzed = models.BooleanField(default=False)
    found = models.BooleanField(default=False)

    def analyze_photo(self):
        #get the image
        response = requests.get(self.large_url)
        img = Image.open(BytesIO(response.content))

        frame = cv2.flip(np.array(img), 1)
        detector = cecbr_photos.photos.utils.FaceDetector.FaceDetector()
        faces = detector.detect_faces(frame,settings.USE_DLIB)
        face_dict = {}
        for n, face in enumerate(faces):
            face_dict[n+1] =face.tolist()
        self.json_data = json.dumps(face_dict)
        self.analyzed = True
        self.save()






    class Meta:
        ordering = ['album', 'id']
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'


class Person(models.Model):
    campuser = models.ForeignKey(CampUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False, null=False)
    photos = models.ManyToManyField(Photo)

    def __str__(self):
        return self.name


class TrainingPhoto(models.Model):
    person = models.ForeignKey(CampUser, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=training_directory_path, null=False, blank=False)
    json_data = models.TextField(blank=True)


class TrainingGroup(models.Model):
    campuser = models.ForeignKey(CampUser, on_delete=models.CASCADE)
    people = models.ManyToManyField(Person)
    trained_svm = models.FilePathField('/home/trainers/svm', match='*.pkl', blank=True, null=True)
    trained_gcc = models.FilePathField('/home/trainers/gcc', match='*.pkl', blank=True, null=True)
    trained = models.BooleanField(default=False)
    trained_date = models.DateTimeField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):
        if not self.trained:
            self.trained_svm = None
            self.trained_gcc = None
            self.trained_date = None
        super(TrainingGroup, self).save(force_insert, force_update, using, update_fields, *args, **kwargs)

    def get_photos(self):

        group_photos = []
        for person in self.people:
            for photo in person.photos:
                group_photos.append(photo)

        return group_photos
