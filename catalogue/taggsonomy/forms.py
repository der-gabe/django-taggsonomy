# -*- coding: utf-8 -*-
from django import forms

from .models import Tag


class TagForm(forms.ModelForm):
    class Meta(object):
        fields = ('name', 'color')
        model = Tag
