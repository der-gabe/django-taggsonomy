# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError

from .errors import TaggsonomyError
from .models import Tag


class TagsField(forms.CharField):

    def to_python(self, value):
        """
        Turn the field value into a set of tags.

        The field value is presumed to be a comma-separated list of tag names.

        Raises ValidationErrors for tag names without existing tags.
        """
        if not value:
            return set()
        names = {name.strip() for name in value.split(',')}
        errors, tags = [], set()
        for name in names:
            try:
                tags.add(Tag.objects.get(name=name))
            except Tag.DoesNotExist:
                errors.append(
                    ValidationError(
                        'No such Tag: %(name)s',
                        code='nosuchtag',
                        params={'name': name}
                    )
                )
        if errors:
            raise ValidationError(errors)
        return tags


class TagForm(forms.ModelForm):

    exclusions = TagsField(required=False)
    subtags = TagsField(required=False)
    supertags = TagsField(required=False)

    class Meta(object):
        fields = ('name', 'color')
        model = Tag

    def _add_subtags(self):
        for subtag in self.cleaned_data.get('subtags'):
            try:
                self.instance.include(subtag)
            except TaggsonomyError:
                # TODO: implement some error handling here
                pass

    def _add_supertags(self):
        for supertag in self.cleaned_data.get('supertags'):
            try:
                supertag.include(self.instance)
            except TaggsonomyError:
                # TODO: implement some error handling here
                pass

    def _exclude_tags(self):
        for tag in self.cleaned_data.get('exclusions'):
            try:
                self.instance.exclude(tag)
            except TaggsonomyError:
                # TODO: implement some error handling here
                pass

    def save(self, *args, **kwargs):
        self._add_subtags()
        self._add_supertags()
        self._exclude_tags()
        return super().save(*args, **kwargs)
