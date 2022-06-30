# -*- coding: utf-8 -*-
from functools import reduce

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from ..errors import MutualExclusionError, MutuallyExclusiveSupertagsError
from .tags import check_mutually_exclusive_tags, Tag


class TagSet(models.Model):
    """
    Collection of tags associated with an object
    """
    _tags = models.ManyToManyField(Tag, related_name='tagsets')
    # Generic relation stuff
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()

    class Meta(object):
        unique_together = ('content_type', 'object_id')

    def __contains__(self, tag):
        return self._tags.filter(id=tag.id).exists()

    def __str__(self):
        return 'TagSet for {}'.format(self.content_object)

    def add(self, *args, create_nonexisting=False):
        """
        Add the given tag(s) to this tag set

        Adding a tag will remove other tags that are excluded by it from this
        tag set.

        One may not add several tags that exclude each other in one call.
        Attempting to do this will raise MutualExclusionError.

        One may also not add several tags that have mutually exclusive supertags
        or where at least one of one tag's supertags is excluded by another tag
        to be added.
        Attempting to do so will raise MutuallyExclusiveSupertagsError.
        """
        kwargs = dict(create_nonexisting=create_nonexisting)
        # First, get tags from positional args, validating them individually
        tags = Tag.objects.get_tags_from_arguments(*args, **kwargs)
        # Next, check that the full set of tags to be added directly does not
        # contain mutually exclusive tags…
        if check_mutually_exclusive_tags(tags):
            raise MutualExclusionError
        # … and that the full set of tags to be added, including all supertags,
        # does not do so either.
        supertags = set(reduce(lambda ts1, ts2: ts1.union(ts2),
                               [tag.get_all_supertags() for tag in tags],
                               Tag.objects.none()))
        combined_tags = set(tags) | supertags
        if check_mutually_exclusive_tags(combined_tags):
            raise MutuallyExclusiveSupertagsError
        # Now remove any present tags that are excluded by tags to be added
        # explicitely.
        for present_tag in self._tags.all():
            for new_tag in combined_tags:
                if new_tag.excludes(present_tag):
                    self._tags.remove(present_tag)
                    break
        # Finally, add the new tags and all the supertags.
        self._tags.add(*combined_tags)

    def all(self, *args, **kwargs):
        return self._tags.all(*args, **kwargs)

    def count(self, *args, **kwargs):
        return self._tags.count(*args, **kwargs)

    def exists(self, *args, **kwargs):
        return self._tags.exists(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self._tags.filter(*args, **kwargs)

    def remove(self, *args):
        """
        Remove the given tag(s) from this tag set
        """
        kwargs = dict(create_nonexisting=False)
        # First, get tags from positional args, validating them individually
        tags = Tag.objects.get_tags_from_arguments(*args, **kwargs)
        self._tags.remove(*tags)
