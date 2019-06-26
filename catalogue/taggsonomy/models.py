from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .errors import (CircularInclusionError, CommonSubtagExclusionError,
                     MutualExclusionError, NoSuchTagError, SelfExclusionError,
                     SimultaneousInclusionExclusionError)


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

    def get_tag_from_argument(self, argument, create_nonexisting=False):
        """
        Return a Tag object from the positional argument, which may be:
        - a tag instances (Tag object),
        - a tag name (Tag.name (str)),
        - or a tag ID (Tag.pk (int)).

        If the argument is a str and no tag by that name exists:
        - raise NoSuchTagError, if create_nonexisting is False
        - create and return such a Tag otherwise.

        raises NoSuchTagError if the argument is an int and no tag with
        such an ID exists.
        """
        if isinstance(argument, Tag):
            # It's already a Tag object, let's just use it.
            return argument
        elif isinstance(argument, str):
            # It's a string, i.e. it should be a tag name...
            if create_nonexisting:
                return self.get_or_create_by_name(argument)
            else:
                return self.get_by_name(argument)
        elif isinstance(argument, int):
            # It's an integer, i.e. it should be the tag's ID.
            try:
                return self.get(pk=argument)
            except Tag.DoesNotExist:
                raise NoSuchTagError
        else:
            # Unsupported type
            raise NoSuchTagError

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
        for argument in args:
            tags.add(
                self.get_tag_from_argument(
                    argument,
                    create_nonexisting=create_nonexisting)
            )
        return tags


class Tag(models.Model):
    _inclusions = models.ManyToManyField('self', symmetrical=False)
    _exclusions = models.ManyToManyField('self')
    name = models.CharField(max_length=256, unique=True)
    objects = TagManager()

    def __str__(self):
        return self.name

    def add_supertags_to_tagset(self, tagset):
        """
        Add this tags supertags (and their supertags etc. ad finitum)
        to the given tagset
        """
        supertags = Tag.objects.filter(_inclusions=self)
        tagset.add(*supertags)
        for supertag in supertags:
            supertag.add_supertags_to_tagset(tagset)

    def add_tag_to_subtagsets(self, tag):
        """
        Add the given tag (instance, id or name) to any tagset
        containing any subtag of this tag.
        """
        for subtag in self._inclusions.all():
            subtag.add_tag_to_tagsets(tag)
            subtag.add_tag_to_subtagsets(tag)

    def add_tag_to_tagsets(self, tag):
        """
        Add the given tag (instance, id or name) to any tagset already
        containing this tag.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        for tagset in TagSet.objects.filter(_tags__id=self.id):
            tagset.add(tag_instance)

    def exclude(self, tag):
        """
        Add the given tag (instance, id or name) to this tag's exclusion set
        and vice versa.

        Tags that exclude each other will never be present in the same tag set.

        A tag may not exclude itself, as that makes no logical sense.
        Attempts to do so will raise a SelfExclusionError.

        A tag may not exclude another tag if both are already jointly present in
        the same TagSet.
        Attempts to do this will raise a MutualExclusionError.

        A tag that includes another tag, or is included by it,
        may not simultaneously exclude said other tag.
        Attempts to do this will raise a SimultaneousInclusionExclusionError.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        if tag_instance == self:
            raise SelfExclusionError
        elif self.includes(tag_instance) or tag_instance.includes(self):
            raise SimultaneousInclusionExclusionError
        elif check_common_subtags(self, tag_instance):
            raise CommonSubtagExclusionError
        elif any([tag_instance in tagset for tagset in self.tagsets.all()]):
            raise MutualExclusionError
        else:
            self._exclusions.add(tag_instance)

    def excludes(self, tag):
        """
        Return True if this tag (instance, id or name) excludes the given tag,
        otherwise False.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        return self._exclusions.filter(id=tag_instance.id).exists()

    def get_all_subtags(self):
        """
        Return a TagQuerySet of this tag's subtags
        and their subtags etc. ad finitum
        """
        subtags = self._inclusions.all()
        all_subtags = Tag.objects.none().union(subtags)
        for tag in subtags.all():
            all_subtags = all_subtags.union(tag.get_all_subtags())
        return all_subtags

    def unexclude(self, tag):
        """
        Remove the given tag (instance, id or name) from this tag's exclusion
        set, if present.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        self._exclusions.remove(tag_instance)

    def include(self, tag, update_tagsets=False):
        """
        Add the given tag (instance, id or name) to this tag's inclusion set,
        i.e. make the given tag a subtag of this one and make this tag a
        supertag of the given tag.

        A tag that includes another tag will always be present in any tag set
        that includes the other tag, unless removed manually at some later
        point.

        A tag may not simultaneously include and exclude another tag.
        Attempts to do this will raise a SimultaneousInclusionExclusionError.

        A chain of inclusions starting from one tag may not loop around back to
        the same tag. Attempts to achieve this will raise a
        CircularInclusionError.

        If `update_tagsets` is True, the included tag's new supertag (this one)
        and all of its supertags will be added to any tag set already containing
        the included tag.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        if tag_instance == self:
            return
        elif self.excludes(tag_instance):
            raise SimultaneousInclusionExclusionError
        elif tag_instance.includes(self):
            raise CircularInclusionError
        self._inclusions.add(tag_instance)
        if update_tagsets:
            tag_instance.add_tag_to_tagsets(self)
            tag_instance.add_tag_to_subtagsets(self)

    def includes(self, tag):
        """
        Return True if this tag (instance, id or name) includes the given tag,
        either directly or indirectly, otherwise False.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        if self._inclusions.filter(id=tag_instance.id).exists():
            return True
        for included_tag in self._inclusions.all():
            if included_tag.includes(tag_instance):
                return True
        return False


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
        # Next, check that the set of tags to be added does not, itself, contain
        # mutually exclusive tags
        if check_mutually_exclusive_tags(tags):
            raise MutualExclusionError
        # Now remove any present tags that are excluded by tags to be added
        for present_tag in self._tags.all():
            for new_tag in tags:
                if new_tag.excludes(present_tag):
                    self._tags.remove(present_tag)
                    break
        # Finally, add the new tags.
        self._tags.add(*tags)
        # Now add all supertags of the tags we just added
        for tag in tags:
            tag.add_supertags_to_tagset(self)

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


def check_mutually_exclusive_tags(tags):
    """
    Check whether the given set of tags contains mutually exclusive tags.

    returns True if that is the case, False otherwise
    """
    found_exclusion = False
    for tag in tags:
        for other_tag in tags - set([tag]):
            if tag.excludes(other_tag):
                found_exclusion = True
                break
    return found_exclusion

def check_common_subtags(*tags):
    """
    Check whether the given tags have at least one common subtag.

    returns True if that is the case, False otherwise
    """
    subtag_sets = set([tag.get_all_subtags() for tag in tags])
    return Tag.objects.intersection(*subtag_sets).exists()
