from django import forms
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
from .models import CampUser


@admin.register(CampUser)
class MyUserAdmin(admin.ModelAdmin):
    model = CampUser
    list_display = ['get_uname','get_name','get_su']
    def get_uname(self,obj):
        return obj.user.username
    def get_name(self,obj):
        return obj.user.name
    def get_su(self,obj):
        return obj.user.is_superuser

    get_name.admin_order_field = 'user'  # Allows column order sorting
    get_name.short_description = 'Name'  # Renames column head

    get_uname.admin_order_field = 'user'  # Allows column order sorting
    get_uname.short_description = 'Username'  # Renames column head

    get_su.admin_order_field = 'user'  # Allows column order sorting
    get_su.short_description = 'Is Superuser'  # Renames column head

    search_fields = ['get_name']
