# -*- coding: utf-8 -*-
import re

from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from .widgets import ColorInputWidget


class ColorField(forms.CharField):
    widget = ColorInputWidget()

    def clean(self, value):
        hex_value = value.lstrip('#')
        rgb_pattern = re.compile('[0-9a-fA-F]{6}')
        if not rgb_pattern.search(hex_value):
            raise ValidationError('Invalid RGB value: {}'.format(value))
        return hex_value

    def prepare_value(self, value):
        return '#' + value
