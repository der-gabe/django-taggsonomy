# -*- coding: utf-8 -*-
from colorinput.models import ColorField
from django.db import models
from django.urls import reverse

from ..errors import (CircularInclusionError, CommonSubtagExclusionError,
                     MutualExclusionError, MutuallyExclusiveSupertagsError,
                     NoSuchTagError, SelfExclusionError,
                     SimultaneousInclusionExclusionError,
                     SupertagAdditionWouldRemoveExcludedError)
from .base import ExclusionTagSet, SubTagSet, SuperTagSet


def check_common_subtags(*tags):
    """
    Check whether the given tags have at least one common subtag.

    returns True if that is the case, False otherwise
    """
    subtag_sets = set([tag.get_all_subtags() for tag in tags])
    return Tag.objects.intersection(*subtag_sets).exists()


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
    color = ColorField(default="d0d0d0")
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
        from .tagsets import TagSet
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

        A tag that includes another tag, or is included by it, even indirectly,
        may not simultaneously exclude said other tag.
        Attempts to do this will raise a SimultaneousInclusionExclusionError.

        A tag may also not exclude another tag if they share common subtag, as
        this would create a situation where a tag could have mutually exclusive
        supertags. Attempts to do this will raise a CommonSubtagExclusionError.
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
        Return True if this tag excludes the given tag (instance, id or name),
        otherwise False.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        return self._exclusions.filter(id=tag_instance.id).exists()

    @property
    def exclusions(self):
        return ExclusionTagSet(self)

    def get_absolute_url(self):
        return reverse('taggsonomy:edit-tag', args=(self.id,))

    def get_all_subtags(self):
        """
        Return a TagQuerySet of this tag's subtags
        and their subtags etc. ad finitum
        """
        direct_subtags = self.get_direct_subtags()
        all_subtags = Tag.objects.none().union(direct_subtags)
        for tag in direct_subtags.all():
            all_subtags = all_subtags.union(tag.get_all_subtags())
        return all_subtags

    def get_all_supertags(self):
        """
        Return a TagQuerySet of this tag's supertags
        and their supertags etc. ad finitum
        """
        direct_supertags = self.get_direct_supertags()
        all_supertags = Tag.objects.none().union(direct_supertags)
        for tag in direct_supertags.all():
            all_supertags = all_supertags.union(tag.get_all_supertags())
        return all_supertags

    def get_direct_subtags(self):
        """
        Return a TagQuerySet of this tag's *direct* subtags,
        i.e. other tags directly included by this one.
        """
        return self._inclusions.all()
        
    def get_direct_supertags(self):
        """
        Return a TagQuerySet of this tag's *direct* supertags,
        i.e. other tags directly including this one.
        """
        return Tag.objects.filter(_inclusions=self)

    def get_excluded_tags(self):
        """
        Return a TagQuerySet of this tag's excluded tags,
        i.e. other tags excluded by (and hence, excluding) this one.
        """
        return self._exclusions.all()

    def get_indirect_subtags(self):
        """
        Return a TagQuerySet of this tag's *indirect* subtags,
        i.e. subtags of this tag's direct subtags, but excluding the direct
        subtags themselves.
        """
        direct_subtags = self.get_direct_subtags()
        all_subtags = self.get_all_subtags()
        return all_subtags.difference(direct_subtags)

    def get_indirect_supertags(self):
        """
        Return a TagQuerySet of this tag's *indirect* supertags,
        i.e. supertags of this tag's direct supertags, but excluding the
        direct supertags themselves.
        """
        direct_supertags = self.get_direct_supertags()
        all_supertags = self.get_all_supertags()
        return all_supertags.difference(direct_supertags)

    def creates_mutually_exclusive_supertags_with_subtag(self, tag):
        """
        Return True if this tag and the given tag (instance, id or name) have
        mutually exclusive supertags, or if this tag directly excludes one of
        the given tag's supertags, or if the given tag directly excludes one of
        this tag's supertags, otherwise False.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        combined_tags = self.get_all_supertags().union(
            tag_instance.get_all_supertags()
        ).union(
            Tag.objects.filter(id__in={self.id, tag.id})
        )
        return check_mutually_exclusive_tags(set(combined_tags))

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

        A tag may also not include another tag with a supertag it itself or one
        of its own supertags excludes, or which is excluded directly by one of
        the tags own supertags, as this would create a situation where a tag
        could potentially have mutually exclusive supertags. Attempts to do this
        will raise a MutuallyExclusiveSupertagsError.

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
        elif self.creates_mutually_exclusive_supertags_with_subtag(tag_instance):
            raise MutuallyExclusiveSupertagsError
        elif update_tagsets:
            # We're required to update all tag sets containing the newly included
            # subtag by adding this (new super)tag and all of its respective
            # supertags, but doing so might lead to the silent removal of other
            # tags from those tag sets, due to exclusion, which must not be
            # allowed to happen.
            # Check whether this tag and all its supertags together exclude any
            # tag in any tag set containing the newly included subtag and throw
            # an exception, if so.
            # 1. Get a set of all supertags (of `self`) and add `self` to it.
            # 2. Get a set of all the tags that are excluded by the above set.
            # 3. Get a set of all tag sets containing the newly included (sub)tag.
            # 4. Get a set of all tags contained in any of the above tag sets.
            # 5. Check if there's any overlap (intersection) between the sets
            #    from 2. and 4. - if there is, raise an error.
            self_set =  Tag.objects.filter(pk=self.pk)
            tags_to_add = self_set.union(self.get_all_supertags())
            tags_excluded_by_tags_to_add = Tag.objects.none()
            for tag_to_add in tags_to_add:
                tags_excluded_by_tags_to_add |= tag_to_add._exclusions.all()
            from .tagsets import TagSet
            subtag_tagsets = TagSet.objects.filter(_tags=tag_instance)
            tags_in_subtag_tagsets = Tag.objects.filter(
                tagsets__in=subtag_tagsets
            )
            if tags_in_subtag_tagsets.intersection(
                    tags_excluded_by_tags_to_add
            ).exists():
                raise SupertagAdditionWouldRemoveExcludedError
        self._inclusions.add(tag_instance)
        if update_tagsets:
            tag_instance.add_tag_to_tagsets(self)
            tag_instance.add_tag_to_subtagsets(self)

    def includes(self, tag):
        """
        Return True if this tag includes the given tag (instance, id or name),
        either directly or indirectly, otherwise False.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        if self._inclusions.filter(id=tag_instance.id).exists():
            return True
        for included_tag in self._inclusions.all():
            if included_tag.includes(tag_instance):
                return True
        return False

    def uninclude(self, tag):
        """
        Remove the given tag (instance, id or name) from this tag's inclusion
        set, if present.
        """
        tag_instance = Tag.objects.get_tag_from_argument(tag)
        self._inclusions.remove(tag_instance)

    @property
    def subtags(self):
        return SubTagSet(self)

    @property
    def supertags(self):
        return SuperTagSet(self)
