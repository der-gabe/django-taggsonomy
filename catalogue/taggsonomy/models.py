from django.db import models

from .errors import NoSuchTagError


class Tag(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class TagSet(models.Model):
    """
    Collection of tags associated with an object
    """
    _tags = models.ManyToManyField(Tag, related_name='tagsets')

    def __contains__(self, tag):
        return self._tags.filter(id=tag.id).exists()

    def _get_tag_from_name(self, name, create_nonexisting=False):
        """
        
        """
        if create_nonexisting:
            # A tag of that name should already exist.
            try:
                tag = Tag.objects.get(name=name)
            except Tag.DoesNotExist:
                raise NoSuchTagError
        else:
            # The tag is not required to exist.
            tag, _ = Tag.objects.get_or_create(name=name)
        return tag

    def _get_tags_from_args(self, *args, create_nonexisting=False):
        """
        Return a set of Tag objects from positional arguments, which may be:
        - tag instances (Tag objects),
        - tag names (Tag.name (str)),
        - or tag IDs (Tag.pk (int)).
        """
        # Also validate tags individually.
        # Collect errors before raising or raise at the first problem encountered?
        # Currently raising at first error...
        tags = set()
        for arg in args:
            if isinstance(arg, Tag):
                # It's already a Tag object, let's just use it.
                tags.add(arg)
            elif isinstance(arg, str):
                # It's a string, i.e. it should be a tag name...
                tags.add(self._get_tag_from_name(arg, create_nonexisting=create_nonexisting))
            elif isinstance(arg, int):
                # It's an integer, i.e. it should be the tag's ID.
                try:
                    tags.add(Tag.objects.get(pk=arg))
                except Tag.DoesNotExist:
                    raise NoSuchTagError
            else:
                # Unsupported type
                raise NoSuchTagError
        return tags                    
            

    def add(self, *args, create_nonexisting=False):
        """
        Add the given tag(s) to this tag set
        """
        # First, get tags from positional args, validating them individually
        tags = self._get_tags_from_args(*args, create_nonexisting=create_nonexisting)
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
        # First, get tags from positional args, validating them individually
        tags = self._get_tags_from_args(*args, create_nonexisting=True)
        self._tags.remove(*tags)
