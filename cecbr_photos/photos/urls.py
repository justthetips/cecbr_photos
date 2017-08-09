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



]


