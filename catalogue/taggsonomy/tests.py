from django.test import TestCase

from .errors import (MutualExclusionError, NoSuchTagError, SelfExclusionError,
                     SimultaneousInclusionExclusionError)
from .models import Tag, TagSet


class TagSetAddBasicTests(TestCase):
    """
    Tests for basic functionality provided by TagSet's `add` method
    """

    def setUp(self):
        self.tag0 = Tag.objects.create(name='foo')
        self.tag1 = Tag.objects.create(name='bar')
        self.tag2 = Tag.objects.create(name='baz')
        self.tagset = TagSet.objects.create()

    def test_add_nothing(self):
        self.tagset.add()
        self.assertFalse(self.tagset.exists())

    def test_add_single_tag_instance(self):
        self.tagset.add(self.tag0)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_single_tag_by_ID(self):
        self.tagset.add(self.tag0.id)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_single_existing_tag_by_name(self):
        self.tagset.add(self.tag0.name)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_single_nonexisting_tag_by_name(self):
        self.tagset.add('foooo', create_nonexisting=True)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 1)
        self.assertTrue(self.tagset.filter(name='foooo').exists())
        self.assertEquals(self.tagset.filter(name='foooo').count(), 1)

    def test_add_single_nonexisting_tag_by_name_ERROR(self):
        with self.assertRaises(NoSuchTagError):
            self.tagset.add('foooo', create_nonexisting=False)
        self.assertFalse(self.tagset.exists())

    def test_add_several_tag_instances(self):
        self.tagset.add(self.tag0, self.tag1, self.tag2)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_add_several_tags_by_ID(self):
        self.tagset.add(self.tag0.id, self.tag1.id, self.tag2.id)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_add_several_existing_tags_by_name(self):
        self.tagset.add(self.tag0.name, self.tag1.name, self.tag2.name)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_add_several_nonexisting_tags_by_name(self):
        """
        Test attempt to add non-existing tags by name when `create_nonexisting=True`
        """
        self.tagset.add('foooo', 'baaar', 'baaaz', create_nonexisting=True)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 3)
        self.assertEquals(self.tagset.filter(name='foooo').count(), 1)
        self.assertEquals(self.tagset.filter(name='baaar').count(), 1)
        self.assertEquals(self.tagset.filter(name='baaaz').count(), 1)

    def test_add_several_nonexisting_tags_by_name_ERROR(self):
        """
        Test attempt to add non-existing tags by name when
        `create_nonexisting=False`, which is the default

        Should not add any tags and instead raise `NoSuchTagError`
        """
        with self.assertRaises(NoSuchTagError):        
            self.tagset.add('foooo', 'baaar', 'baaaz')
        self.assertFalse(self.tagset.exists())

    def test_add_several_tags_by_name(self):
        """
        Test addition of existing and non-existing tags by name when
        `create_nonexisting=True`
        """
        self.tagset.add(
            self.tag0.name, self.tag1.name, self.tag2.name,
            'foooo', 'baaar', 'baaaz', create_nonexisting=True
        )
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 6)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)
        self.assertTrue(self.tagset
                            .filter(name__in=['foooo', 'baaar', 'baaaz'])
                            .exists())
        self.assertEquals(self.tagset.filter(name='foooo').count(), 1)
        self.assertEquals(self.tagset.filter(name='baaar').count(), 1)
        self.assertEquals(self.tagset.filter(name='baaaz').count(), 1)

    def test_add_several_tags_by_name_ERROR(self):
        """
        Test attempt to add existing and non-existing tags by name when
        `create_nonexisting=False`, which is the default

        Should not add any tags and instead raise `NoSuchTagError`
        """
        with self.assertRaises(NoSuchTagError):        
            self.tagset.add(
                self.tag0.name, self.tag1.name, self.tag2.name,
                'foooo', 'baaar', 'baaaz'
            )
        self.assertFalse(self.tagset.exists())

    def test_add_several_tags(self):
        """
        Test addition of several tags at once by different types:
        - Tag (instance),
        - int (ID) and
        - str (name),
        including a non-existing tag by name (str) with `create_nonexisting=True`
        """
        self.tagset.add(self.tag0, self.tag1.id, self.tag2.name, 'foooo',
                        create_nonexisting=True)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 4)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)
        self.assertTrue(self.tagset.filter(name='foooo').exists())
        self.assertEquals(self.tagset.filter(name='foooo').count(), 1)

    def test_add_several_tags_ERROR(self):
        """
        Test attempt to add several tags at once by different types:
        - Tag (instance),
        - int (ID) and
        - str (name),
        including a non-existing tag by name (str) with
        `create_nonexisting=False`, which is the default

        Should not add any tags and instead raise `NoSuchTagError`
        """
        with self.assertRaises(NoSuchTagError):        
            self.tagset.add(self.tag0, self.tag1.id, self.tag2.name, 'foooo')
        self.assertFalse(self.tagset.exists())

    def test_add_same_tag_twice_simultaneously_by_instance(self):
        self.tagset.add(self.tag0, self.tag0)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_same_tag_thrice_simultaneously(self):
        self.tagset.add(self.tag0, self.tag0.id, self.tag0.name)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_same_tag_thrice_sequentially(self):
        self.tagset.add(self.tag0)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

        self.tagset.add(self.tag0.id)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

        self.tagset.add(self.tag0.name)
        self.assertTrue(self.tagset.exists())
        self.assertEquals(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)


class ExclusionSetupMixin(object):
    """
    Mixin to provide common setUp method for exclusion test cases
    """

    def setUp(self):
        self.tag0 = Tag.objects.create(name='foo')
        self.tag1 = Tag.objects.create(name='bar')
        self.tag2 = Tag.objects.create(name='baz')
        # Let tag0 exclude both other tags: tag1 *and* tag2
        self.tag0._exclusions.add(self.tag1, self.tag2)
        # Note that this does *not* mean that tag1 excludes tag2, or vice versa


class TagExclusionTests(ExclusionSetupMixin, TestCase):
    """
    Tests for Tag model's exclusion mechanism
    """

    def test_exclusion_relation_forwards(self):
        self.assertEquals(self.tag0._exclusions.count(), 2)
        self.assertTrue(self.tag0._exclusions.filter(id=self.tag1.id).exists())
        self.assertTrue(self.tag0._exclusions.filter(id=self.tag2.id).exists())

    def test_exclusion_relation_backwards(self):
        self.assertEquals(self.tag1._exclusions.count(), 1)
        self.assertTrue(self.tag1._exclusions.filter(id=self.tag0.id).exists())
        self.assertEquals(self.tag2._exclusions.count(), 1)
        self.assertTrue(self.tag2._exclusions.filter(id=self.tag0.id).exists())

    def test_exclusion_relation_does_not_affect_exclusion_relation_between_third_tags(self):
        self.assertFalse(self.tag1._exclusions.filter(id=self.tag2.id).exists())
        self.assertFalse(self.tag2._exclusions.filter(id=self.tag1.id).exists())

    def test_exclude_method_with_tag_id(self):
        self.tag1.exclude(self.tag2.id)
        self.assertTrue(self.tag1._exclusions.filter(id=self.tag2.id).exists())
        self.assertTrue(self.tag2._exclusions.filter(id=self.tag1.id).exists())

    def test_exclude_method_with_tag_instance(self):
        self.tag1.exclude(self.tag2)
        self.assertTrue(self.tag1._exclusions.filter(id=self.tag2.id).exists())
        self.assertTrue(self.tag2._exclusions.filter(id=self.tag1.id).exists())

    def test_exclude_method_with_tag_name(self):
        self.tag1.exclude(self.tag2.name)
        self.assertTrue(self.tag1._exclusions.filter(id=self.tag2.id).exists())
        self.assertTrue(self.tag2._exclusions.filter(id=self.tag1.id).exists())

    def test_tag_may_not_exclude_itself(self):
        """
        Self-exclusion is logical nonsense and must be prevented.
        """
        with self.assertRaises(SelfExclusionError):
            self.tag0.exclude(self.tag0)
        self.assertEquals(self.tag0._exclusions.count(), 2)
        self.assertFalse(self.tag0._exclusions.filter(id=self.tag0.id).exists())
        self.assertFalse(self.tag0.excludes(self.tag0))

    def test_excludes_method_forwards_with_tag_ids(self):
        self.assertTrue(self.tag0.excludes(self.tag1.id))
        self.assertTrue(self.tag0.excludes(self.tag2.id))

    def test_excludes_method_forwards_with_tag_instances(self):
        self.assertTrue(self.tag0.excludes(self.tag1))
        self.assertTrue(self.tag0.excludes(self.tag2))

    def test_excludes_method_forwards_with_tag_names(self):
        self.assertTrue(self.tag0.excludes(self.tag1.name))
        self.assertTrue(self.tag0.excludes(self.tag2.name))

    def test_excludes_method_backwards_with_tag_ids(self):
        self.assertTrue(self.tag1.excludes(self.tag0.id))
        self.assertTrue(self.tag2.excludes(self.tag0.id))

    def test_excludes_method_backwards_with_tag_instances(self):
        self.assertTrue(self.tag1.excludes(self.tag0))
        self.assertTrue(self.tag2.excludes(self.tag0))

    def test_excludes_method_backwards_with_tag_names(self):
        self.assertTrue(self.tag1.excludes(self.tag0.name))
        self.assertTrue(self.tag2.excludes(self.tag0.name))

    def test_excludes_method_for_third_tags_with_tag_ids(self):
        self.assertFalse(self.tag1.excludes(self.tag2.id))
        self.assertFalse(self.tag2.excludes(self.tag1.id))

    def test_excludes_method_for_third_tags_with_tag_instances(self):
        self.assertFalse(self.tag1.excludes(self.tag2))
        self.assertFalse(self.tag2.excludes(self.tag1))

    def test_excludes_method_for_third_tags_with_tag_names(self):
        self.assertFalse(self.tag1.excludes(self.tag2.name))
        self.assertFalse(self.tag2.excludes(self.tag1.name))

    def test_tag_cannot_exclude_other_tag_when_both_already_jointly_present_in_same_tagset(self):
        # Create a TagSet and add two tags that *don't* exclude each other (yet).
        self.tagset = TagSet.objects.create()
        self.tagset.add(self.tag1, self.tag2)
        # Now try to have one tag exclude the other - this should fail!
        with self.assertRaises(MutualExclusionError):
            self.tag1.exclude(self.tag2)
        with self.assertRaises(MutualExclusionError):
            self.tag1.exclude(self.tag2.id)
        with self.assertRaises(MutualExclusionError):
            self.tag1.exclude(self.tag2.name)
        with self.assertRaises(MutualExclusionError):
            self.tag2.exclude(self.tag1)
        with self.assertRaises(MutualExclusionError):
            self.tag2.exclude(self.tag1.id)
        with self.assertRaises(MutualExclusionError):
            self.tag2.exclude(self.tag1.name)

    def test_unexclude_method_with_tag_id(self):
        self.tag0.unexclude(self.tag1.id)
        self.assertFalse(self.tag0._exclusions.filter(id=self.tag1.id).exists())
        self.assertFalse(self.tag1._exclusions.filter(id=self.tag0.id).exists())

    def test_unexclude_method_with_tag_instance(self):
        self.tag0.unexclude(self.tag1)
        self.assertFalse(self.tag0._exclusions.filter(id=self.tag1.id).exists())
        self.assertFalse(self.tag1._exclusions.filter(id=self.tag0.id).exists())

    def test_unexclude_method_with_tag_name(self):
        self.tag0.unexclude(self.tag1.name)
        self.assertFalse(self.tag0._exclusions.filter(id=self.tag1.id).exists())
        self.assertFalse(self.tag1._exclusions.filter(id=self.tag0.id).exists())

    def test_exclude_included_tag_ERROR(self):
        """
        A tag cannot simultaneously include and exclude another.
        """
        self.tag1._inclusions.add(self.tag2)
        with self.assertRaises(SimultaneousInclusionExclusionError):
            self.tag1.exclude(self.tag2)
        with self.assertRaises(SimultaneousInclusionExclusionError):
            self.tag2.exclude(self.tag1)


class TagSetExclusionTests(ExclusionSetupMixin, TestCase):
    """
    Tests for TagSet model's handling of tag exclusions
    """

    def setUp(self):
        super(TagSetExclusionTests, self).setUp()
        self.tagset = TagSet.objects.create()

    def test_adding_mutually_exclusive_tags_ERROR(self):
        with self.assertRaises(MutualExclusionError):
            self.tagset.add(self.tag0, self.tag1)
        self.assertFalse(self.tagset.exists())

    def test_adding_tag_excluded_by_already_present_tag(self):
        self.tagset.add(self.tag0)
        self.tagset.add(self.tag1)
        self.assertEquals(self.tagset.count(), 1)
        self.assertTrue(self.tag1 in self.tagset)


class TagSetRemoveTests(TestCase):
    """
    Tests for basic functionality provided by TagSet's `remove` method
    """

    def setUp(self):
        self.tag0 = Tag.objects.create(name='foo')
        self.tag1 = Tag.objects.create(name='bar')
        self.tag2 = Tag.objects.create(name='baz')
        self.tagset = TagSet.objects.create()
        self.tagset._tags.add(self.tag0, self.tag1, self.tag2)

    def test_remove_nothing(self):
        self.tagset.remove()
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_single_tag_instance(self):
        self.assertEquals(self.tagset.count(), 3)
        self.tagset.remove(self.tag0)
        self.assertEquals(self.tagset.count(), 2)
        self.assertNotIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_single_tag_by_ID(self):
        self.assertEquals(self.tagset.count(), 3)
        self.tagset.remove(self.tag1.id)
        self.assertEquals(self.tagset.count(), 2)
        self.assertIn(self.tag0, self.tagset)
        self.assertNotIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_single_nonexisting_tag_by_ID_ERROR(self):
        self.assertEquals(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag0.id + self.tag1.id + self.tag2.id)
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_single_tag_by_name(self):
        self.assertEquals(self.tagset.count(), 3)
        self.tagset.remove(self.tag2.name)
        self.assertEquals(self.tagset.count(), 2)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertNotIn(self.tag2, self.tagset)

    def test_remove_single_nonexisting_tag_by_name_ERROR(self):
        self.assertEquals(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove('foooo')
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tag_instances(self):
        self.assertEquals(self.tagset.count(), 3)
        self.tagset.remove(self.tag0, self.tag1)
        self.assertEquals(self.tagset.count(), 1)
        self.assertNotIn(self.tag0, self.tagset)
        self.assertNotIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tags_by_ID(self):
        self.assertEquals(self.tagset.count(), 3)
        self.tagset.remove(self.tag1.id, self.tag2.id)
        self.assertEquals(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)
        self.assertNotIn(self.tag1, self.tagset)
        self.assertNotIn(self.tag2, self.tagset)

    def test_remove_several_tags_incl_nonexisting_by_ID_ERROR(self):
        self.assertEquals(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag1.id, self.tag2.id,
                               self.tag1.id + self.tag2.id)
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tags_by_name(self):
        self.assertEquals(self.tagset.count(), 3)
        self.tagset.remove(self.tag0.name, self.tag2.name)
        self.assertEquals(self.tagset.count(), 1)
        self.assertNotIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertNotIn(self.tag2, self.tagset)

    def test_remove_several_tags_incl_nonexisting_by_name_ERROR(self):
        self.assertEquals(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag0.name, self.tag2.name, 'foooo')
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tags(self):
        self.assertEquals(self.tagset.count(), 3)
        self.tagset.remove(self.tag0, self.tag1.id, self.tag2.name)
        self.assertFalse(self.tagset.exists())

    def test_remove_several_tags_incl_nonexisting_ID_ERROR(self):
        self.assertEquals(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag0, self.tag1.id, self.tag2.name, 5)
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tags_incl_nonexisting_name_ERROR(self):
        self.assertEquals(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag0, self.tag1.id, self.tag2.name, 'fooo')
        self.assertEquals(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_same_tag_thrice_simultaneously(self):
        self.assertEquals(self.tagset.count(), 3)
        self.tagset.remove(self.tag0, self.tag0.id, self.tag0.name)
        self.assertEquals(self.tagset.count(), 2)
        self.assertNotIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_same_tag_thrice_simultaneously(self):
        self.assertEquals(self.tagset.count(), 3)
        self.tagset.remove(self.tag0)
        self.tagset.remove(self.tag0.id)
        self.tagset.remove(self.tag0.name)
        self.assertEquals(self.tagset.count(), 2)
        self.assertNotIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)


class InclusionSetupMixin(object):
    """
    Mixin to provide common setUp method for inclusion test cases
    """

    def setUp(self):
        self.supertag = Tag.objects.create(name='Programming')
        self.subtag0 = Tag.objects.create(name='Python')
        self.subtag1 = Tag.objects.create(name='JavaScript')
        self.subtag0._inclusions.add(self.supertag)


class TagInclusionTests(InclusionSetupMixin, TestCase):
    """
    Test for Tag model's inclusion mechanism
    """

    def test_inclusion_relation(self):
        self.assertEquals(self.subtag0._inclusions.count(), 1)
        self.assertEquals(self.subtag1._inclusions.count(), 0)
        self.assertEquals(self.supertag._inclusions.count(), 0)
        self.assertTrue(self.subtag0._inclusions.filter(id=self.supertag.id).exists())
        self.assertFalse(self.supertag._inclusions.filter(id=self.subtag0.id).exists())

    def test_include_method_with_tag_id(self):
        self.assertEquals(self.subtag1._inclusions.count(), 0)
        self.assertEquals(self.supertag._inclusions.count(), 0)
        self.subtag1.include(self.supertag.id)
        self.assertEquals(self.subtag1._inclusions.count(), 1)
        self.assertEquals(self.supertag._inclusions.count(), 0)
        self.assertTrue(self.subtag1._inclusions.filter(id=self.supertag.id).exists())
        self.assertFalse(self.supertag._inclusions.filter(id=self.subtag1.id).exists())

    def test_include_method_with_tag_instance(self):
        self.assertEquals(self.subtag1._inclusions.count(), 0)
        self.assertEquals(self.supertag._inclusions.count(), 0)
        self.subtag1.include(self.supertag)
        self.assertEquals(self.subtag1._inclusions.count(), 1)
        self.assertEquals(self.supertag._inclusions.count(), 0)
        self.assertTrue(self.subtag1._inclusions.filter(id=self.supertag.id).exists())
        self.assertFalse(self.supertag._inclusions.filter(id=self.subtag1.id).exists())

    def test_include_method_with_tag_name(self):
        self.assertEquals(self.subtag1._inclusions.count(), 0)
        self.assertEquals(self.supertag._inclusions.count(), 0)
        self.subtag1.include(self.supertag.name)
        self.assertEquals(self.subtag1._inclusions.count(), 1)
        self.assertEquals(self.supertag._inclusions.count(), 0)
        self.assertTrue(self.subtag1._inclusions.filter(id=self.supertag.id).exists())
        self.assertFalse(self.supertag._inclusions.filter(id=self.subtag1.id).exists())

    def test_self_inclusion_does_nothing(self):
        """
        A tag including itself, while not an error, is rather meaningless.

        Attempting to do that should just have no effect at all.
        """
        self.assertEquals(self.subtag1._inclusions.count(), 0)
        self.subtag1.include(self.subtag1)
        self.assertEquals(self.subtag1._inclusions.count(), 0)
        self.assertFalse(self.subtag1._inclusions.filter(id=self.subtag1.id).exists())

    def test_include_excluded_tag_ERROR(self):
        """
        A tag cannot simultaneously include and exclude another.
        """
        self.subtag0.exclude(self.subtag1)
        with self.assertRaises(SimultaneousInclusionExclusionError):
            self.subtag0.include(self.subtag1)
        with self.assertRaises(SimultaneousInclusionExclusionError):
            self.subtag1.include(self.subtag0)

    def test_includes_method_with_tag_ids(self):
        self.assertTrue(self.subtag0.includes(self.supertag.id))
        self.assertFalse(self.subtag1.includes(self.supertag.id))
        self.assertFalse(self.supertag.includes(self.subtag0.id))
        self.assertFalse(self.supertag.includes(self.subtag1.id))

    def test_includes_method_with_tag_instances(self):
        self.assertTrue(self.subtag0.includes(self.supertag))
        self.assertFalse(self.subtag1.includes(self.supertag))
        self.assertFalse(self.supertag.includes(self.subtag0))
        self.assertFalse(self.supertag.includes(self.subtag1))

    def test_includes_method_with_tag_names(self):
        self.assertTrue(self.subtag0.includes(self.supertag.name))
        self.assertFalse(self.subtag1.includes(self.supertag.name))
        self.assertFalse(self.supertag.includes(self.subtag0.name))
        self.assertFalse(self.supertag.includes(self.subtag1.name))

    # TODO: Test that letting tag A include tag B adds tag B to any tag set that A is already a part of.
    # TODO: Test that a tag may not simultaneously include mutually exclusive tags.
    # TODO: Test that circular inclusions are not allowed


class TagSetInclusionTests(InclusionSetupMixin, TestCase):
    """
    Tests for TagSet model's handling of tag inclusions
    """

    def setUp(self):
        super(TagSetInclusionTests, self).setUp()
        self.tagset = TagSet.objects.create()

    def test_adding_tag_that_includes_other_tag_adds_both(self):
        self.assertEquals(self.tagset.count(), 0)
        self.tagset.add(self.subtag0)
        self.assertTrue(self.subtag0 in self.tagset)
        self.assertEquals(self.tagset.count(), 2)
        self.assertTrue(self.supertag in self.tagset)

    # TODO: Test inclusion chain, e.g. Django includes Python includes Programming
