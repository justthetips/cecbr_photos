
import os
from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
# Setup django project
django.setup()

app = Celery('cecbr_photos')
app.config_from_object('django.conf:settings', namespace='CELERY')

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # pragma: no cover


