from django.contrib import admin
from .models import CampUser, Season, Album, Photo
import json


@admin.register(CampUser)
class MyUserAdmin(admin.ModelAdmin):
    model = CampUser
    list_display = ['get_uname', 'get_name', 'get_su']

    def get_uname(self, obj):
        return obj.user.username

    def get_name(self, obj):
        return obj.user.name

    def get_su(self, obj):
        return obj.user.is_superuser

    get_name.admin_order_field = 'user'  # Allows column order sorting
    get_name.short_description = 'Name'  # Renames column head

    get_uname.admin_order_field = 'user'  # Allows column order sorting
    get_uname.short_description = 'Username'  # Renames column head

    get_su.admin_order_field = 'user'  # Allows column order sorting
    get_su.short_description = 'Is Superuser'  # Renames column head

    search_fields = ['get_name']


def handle_season(modeladmin, request, queryset):
    cu = request.user.campuser
    for season in queryset:
        season.process_season(cu)


def handle_album(modeladmin, request, queryset):
    cu = request.user.campuser
    for album in queryset:
        album.process_album(cu)


def analyze_album(modeladmin, request, queryset):
    cu = request.user.campuser
    for album in queryset:
        photos = Photo.objects.filter(album=album)
        for photo in photos:
            photo.analyze_photo()

        album.analyzed = True
        album.save()

def analyze_photo(modeladmin, request, queryset):
    for photo in queryset:
        photo.analyze_photo()



@admin.register(Season)
class MySeasonAdmin(admin.ModelAdmin):
    model = Season
    list_display = ('season_name', 'album_count')
    actions = [handle_season]


@admin.register(Album)
class MyAlbumAdmin(admin.ModelAdmin):
    model = Album
    list_display = ('name', 'season', 'count', 'date', 'processed', 'analyzed')
    actions = [handle_album, analyze_album]

@admin.register(Photo)
class MyPhotoAdmin(admin.ModelAdmin):
    model = Photo
    list_display = ('id', 'album', 'analyzed', 'found', 'analyzed_date', 'found_date', 'downloaded' )
    actions = [analyze_photo]
    list_filter = ('album',)
