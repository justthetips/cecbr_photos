from PIL import Image
import json
import requests
from io import BytesIO
from cecbr_photos.photos.models import TrainingPhoto, Photo


class CEImage(object):


    def __index__(self, photo):
        if isinstance(photo, TrainingPhoto):
            self._url = TrainingPhoto.photo.url
        elif isinstance(photo, Photo):
            self._url = Photo.large_url
        else:
            raise ValueError("Must be a training photo or Photo, not a {}".format(photo.__class__))

        response = requests.get(self._url)
        self._img = Image.open(BytesIO(response.content))
        self._json = photo.json_data

    @property
    def size(self):
        return self._img.size


    @property
    def height(self):
        return self.size[1]

    @property
    def width(self):
        return self.size[0]

    def get_boxes(self):
        mdata = json.loads(self._json)
        return mdata['faces']

    def get_people_boxes(self):
        mdata = json.loads(self._json)
        return mdata['people']
