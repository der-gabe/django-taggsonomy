# -*- coding: utf-8 -*-
"""
Taggsonomy URL Configuration
"""

from django.urls import path

from .views import add_tags, remove_tag_from

app_name = 'taggsonomy'

urlpatterns = [
    path('tag/<int:tag_id>/remove_from/<int:tagset_id>', remove_tag_from, name='remove-tag'),
    path('tags/<int:tagset_id>/add', add_tags, name='add-tags'),
]
