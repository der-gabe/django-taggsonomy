# -*- coding: utf-8 -*-
"""
Taggsonomy URL Configuration
"""

from django.urls import path

from .views import add_tags, remove_tag

app_name = 'taggsonomy'

urlpatterns = [
    path('tags/<int:tagset_id>/add', add_tags, name='add-tags'),
    path('tags/<int:tagset_id>/remove/<int:tag_id>', remove_tag, name='remove-tag'),
]
