import json
from io import BytesIO

import requests
from PIL import Image

from cecbr_photos.photos.models import TrainingPhoto, Photo


class CEImage(object):


    def __init__(self, photo):
        if isinstance(photo, TrainingPhoto):
            self._photo = TrainingPhoto.objects.get(id=photo.id)
            self._url = self._photo.photo.url
            self._json = self._photo.json_data
        elif isinstance(photo, Photo):
            self._photo = Photo.objects.get(id=photo.id)
            self._url = self._photo.large_url
            self._json = self._photo.json_data
        else:
            raise ValueError("Must be a training photo or Photo, not a {}".format(photo.__class__))

        response = requests.get(self._url)
        self._img = Image.open(BytesIO(response.content))


    @property
    def size(self):
        return self._img.size


    @property
    def height(self):
        return self.size[1]

    @property
    def width(self):
        return self.size[0]

    @property
    def url(self):
        return self._url

    def get_boxes(self):
        if self._json is None:
            return []
        else:
            mdata = json.loads(self._json)
            return mdata['faces']

    def get_people_boxes(self):
        mdata = json.loads(self._json)
        return mdata['people']
