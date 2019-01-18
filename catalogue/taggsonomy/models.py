from django.db import models

from .errors import NoSuchTagError


class Tag(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class TagSet(models.Model):
    """
    Collection of tags associated with an object
    """
    _tags = models.ManyToManyField(Tag, related_name='tagsets')

    def __call__(self):
        """
        Return tags contained in this tag set
        """
        # Should we return a list of tag objects or a QuerySet?
        return self._tags

    def _get_tag_from_name(self, name, must_exist=False):
        """
        
        """
        if must_exist:
            # A tag of that name should already exist.
            try:
                tag = Tag.objects.get(name=name)
            except Tag.DoesNotExist:
                raise NoSuchTagError
        else:
            # The tag is not required to exist.
            tag, _ = Tag.objects.get_or_create(name=name)
        return tag

    def _get_tags_from_args(self, *args, must_exist=False):
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
                tags.add(self._get_tag_from_name(arg, must_exist=must_exist))
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
            

    def add(self, *args, auto_remove=True, only_existing=False):
        """
        Add the given tag(s) to this tag set
        """
        # First, get tags from positional args, validating them individually
        tags = self._get_tags_from_args(*args, must_exist=only_existing)
        self._tags.add(*tags)
        # TODO: What should this method return?
