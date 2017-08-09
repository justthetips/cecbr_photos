from django.apps import AppConfig


class PhotosConfig(AppConfig):
    name = 'cecbr_photos.photos'
    verbose_name = "Photos"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
