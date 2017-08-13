from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


from . import views

app_name = 'photos'

urlpatterns = [
    url(
        regex=r'^$',
        view=TemplateView.as_view(template_name='photos/photos_index.html'),
    ),
    url(regex=r'^album/$',
        view=views.album_index,
        name='album_index'
    ),
    url(regex=r'^album/(?P<album_id>[0-9]+)/$',
        view=views.album_view,
        name='album_view'
    ),
    url(regex=r'^photo/(?P<photo_id>[0-9]+)/$',
        view=views.photo_view,
        name='photo_view'
    ),

]


