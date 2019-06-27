# -*- coding: utf-8 -*-
"""
Taggsonomy URL Configuration
"""

from django.urls import path

from .views import (add_tags, remove_tag, TagCreateView, TagDeleteView,
                    TagEditView, TagListView)

app_name = 'taggsonomy'

urlpatterns = [
    path('', TagListView.as_view(), name='tag-list'),
    path('create', TagCreateView.as_view(), name='create-tag'),
    path('<int:pk>', TagEditView.as_view(), name='edit-tag'),
    path('<int:pk>/delete', TagDeleteView.as_view(), name='delete-tag'),
    path('<int:tagset_id>/add', add_tags, name='add-tags'),
    path('<int:tagset_id>/remove/<int:tag_id>', remove_tag, name='remove-tag'),
]
