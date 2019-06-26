# -*- coding: utf-8 -*-
"""
Taggsonomy URL Configuration
"""

from django.urls import path

from .views import add_tags, remove_tag, TagDetailView, TagListView

app_name = 'taggsonomy'

urlpatterns = [
    path('', TagListView.as_view(), name='tag-list'),
    path('<int:pk>', TagDetailView.as_view(), name='tag-detail'),
    path('<int:tagset_id>/add', add_tags, name='add-tags'),
    path('<int:tagset_id>/remove/<int:tag_id>', remove_tag, name='remove-tag'),
]
