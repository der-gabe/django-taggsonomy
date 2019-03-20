from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .errors import NoSuchTagError, SelfExclusionError


class TagManager(models.Manager):

    def get_by_name(self, name):
        """
        Return the Tag with the given name

        raises NoSuchTagError, if no tag by that name exists
        """
        try:
            return self.get(name=name)
        except Tag.DoesNotExist:
            raise NoSuchTagError

    def get_or_create_by_name(self, name):
        """
        Return a Tag with the given name

        creates a Tag, if no tag by that name exists
        """
        tag, _ = self.get_or_create(name=name)
        return tag

    def get_tags_from_arguments(self, *args, create_nonexisting=False):
        """
        Return a set of Tag objects from positional arguments, which may be:
        - tag instances (Tag objects),
        - tag names (Tag.name (str)),
        - or tag IDs (Tag.pk (int)).
        """
        # Also validate tags individually.
        # Collect errors before raising or raise at the first problem
        # encountered? Currently raises at first error...
        tags = set()
        for arg in args:
            if isinstance(arg, Tag):
                # It's already a Tag object, let's just use it.
                tags.add(arg)
            elif isinstance(arg, str):
                # It's a string, i.e. it should be a tag name...
                if create_nonexisting:
                    tags.add(self.get_or_create_by_name(arg))
                else:
                    tags.add(self.get_by_name(arg))
            elif isinstance(arg, int):
                # It's an integer, i.e. it should be the tag's ID.
                try:
                    tags.add(self.get(pk=arg))
                except Tag.DoesNotExist:
                    raise NoSuchTagError
            else:
                # Unsupported type
                raise NoSuchTagError
        return tags


class Tag(models.Model):
    _exclusions = models.ManyToManyField('self')
    name = models.CharField(max_length=256, unique=True)
    objects = TagManager()

    def __str__(self):
        return self.name

    def exclude(self, tag):
        """
        Add the given tag to this tag's exclusion list and vice versa.

        Tags that exclude each other will never be present in the same tag set.

        A tag may not exclude itself, as that makes no logical sense.
        Attempts to do so will raise a SelfExclusionError.
        """
        if tag != self:
            self._exclusions.add(tag)
        else:
            raise SelfExclusionError


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
        """
        kwargs = dict(create_nonexisting=create_nonexisting)
        # First, get tags from positional args, validating them individually
        tags = Tag.objects.get_tags_from_arguments(*args, **kwargs)
        self._tags.add(*tags)
        # TODO: What should this method return?

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
