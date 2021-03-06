from django.test import TestCase

from django_taggsonomy.errors import (
    CircularInclusionError, CommonSubtagExclusionError, MutualExclusionError,
    MutuallyExclusiveSupertagsError, NoSuchTagError, SelfExclusionError,
    SimultaneousInclusionExclusionError,
    SupertagAdditionWouldRemoveExcludedError)
from django_taggsonomy.models import Tag, TagSet


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
        self.assertEqual(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_single_tag_by_ID(self):
        self.tagset.add(self.tag0.id)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_single_existing_tag_by_name(self):
        self.tagset.add(self.tag0.name)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_single_nonexisting_tag_by_name(self):
        self.tagset.add('foooo', create_nonexisting=True)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 1)
        self.assertTrue(self.tagset.filter(name='foooo').exists())
        self.assertEqual(self.tagset.filter(name='foooo').count(), 1)

    def test_add_single_nonexisting_tag_by_name_ERROR(self):
        with self.assertRaises(NoSuchTagError):
            self.tagset.add('foooo', create_nonexisting=False)
        self.assertFalse(self.tagset.exists())

    def test_add_several_tag_instances(self):
        self.tagset.add(self.tag0, self.tag1, self.tag2)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_add_several_tags_by_ID(self):
        self.tagset.add(self.tag0.id, self.tag1.id, self.tag2.id)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_add_several_existing_tags_by_name(self):
        self.tagset.add(self.tag0.name, self.tag1.name, self.tag2.name)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_add_several_nonexisting_tags_by_name(self):
        """
        Test attempt to add non-existing tags by name when `create_nonexisting=True`
        """
        self.tagset.add('foooo', 'baaar', 'baaaz', create_nonexisting=True)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 3)
        self.assertEqual(self.tagset.filter(name='foooo').count(), 1)
        self.assertEqual(self.tagset.filter(name='baaar').count(), 1)
        self.assertEqual(self.tagset.filter(name='baaaz').count(), 1)

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
        self.assertEqual(self.tagset.count(), 6)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)
        self.assertTrue(self.tagset
                            .filter(name__in=['foooo', 'baaar', 'baaaz'])
                            .exists())
        self.assertEqual(self.tagset.filter(name='foooo').count(), 1)
        self.assertEqual(self.tagset.filter(name='baaar').count(), 1)
        self.assertEqual(self.tagset.filter(name='baaaz').count(), 1)

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
        self.assertEqual(self.tagset.count(), 4)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)
        self.assertTrue(self.tagset.filter(name='foooo').exists())
        self.assertEqual(self.tagset.filter(name='foooo').count(), 1)

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
        self.assertEqual(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_same_tag_thrice_simultaneously(self):
        self.tagset.add(self.tag0, self.tag0.id, self.tag0.name)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

    def test_add_same_tag_thrice_sequentially(self):
        self.tagset.add(self.tag0)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

        self.tagset.add(self.tag0.id)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)

        self.tagset.add(self.tag0.name)
        self.assertTrue(self.tagset.exists())
        self.assertEqual(self.tagset.count(), 1)
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
        self.assertEqual(self.tag0._exclusions.count(), 2)
        self.assertTrue(self.tag0._exclusions.filter(id=self.tag1.id).exists())
        self.assertTrue(self.tag0._exclusions.filter(id=self.tag2.id).exists())

    def test_exclusion_relation_backwards(self):
        self.assertEqual(self.tag1._exclusions.count(), 1)
        self.assertTrue(self.tag1._exclusions.filter(id=self.tag0.id).exists())
        self.assertEqual(self.tag2._exclusions.count(), 1)
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
        self.assertEqual(self.tag0._exclusions.count(), 2)
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

    def test_get_excluded_tags_method(self):
        self.assertEqual({*self.tag0.get_excluded_tags()},
                          {self.tag1, self.tag2})
        self.assertEqual({*self.tag1.get_excluded_tags()},
                          {self.tag0})
        self.assertEqual({*self.tag2.get_excluded_tags()},
                          {self.tag0})

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
        self.assertEqual(self.tagset.count(), 1)
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
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_single_tag_instance(self):
        self.assertEqual(self.tagset.count(), 3)
        self.tagset.remove(self.tag0)
        self.assertEqual(self.tagset.count(), 2)
        self.assertNotIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_single_tag_by_ID(self):
        self.assertEqual(self.tagset.count(), 3)
        self.tagset.remove(self.tag1.id)
        self.assertEqual(self.tagset.count(), 2)
        self.assertIn(self.tag0, self.tagset)
        self.assertNotIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_single_nonexisting_tag_by_ID_ERROR(self):
        self.assertEqual(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag0.id + self.tag1.id + self.tag2.id)
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_single_tag_by_name(self):
        self.assertEqual(self.tagset.count(), 3)
        self.tagset.remove(self.tag2.name)
        self.assertEqual(self.tagset.count(), 2)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertNotIn(self.tag2, self.tagset)

    def test_remove_single_nonexisting_tag_by_name_ERROR(self):
        self.assertEqual(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove('foooo')
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tag_instances(self):
        self.assertEqual(self.tagset.count(), 3)
        self.tagset.remove(self.tag0, self.tag1)
        self.assertEqual(self.tagset.count(), 1)
        self.assertNotIn(self.tag0, self.tagset)
        self.assertNotIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tags_by_ID(self):
        self.assertEqual(self.tagset.count(), 3)
        self.tagset.remove(self.tag1.id, self.tag2.id)
        self.assertEqual(self.tagset.count(), 1)
        self.assertIn(self.tag0, self.tagset)
        self.assertNotIn(self.tag1, self.tagset)
        self.assertNotIn(self.tag2, self.tagset)

    def test_remove_several_tags_incl_nonexisting_by_ID_ERROR(self):
        self.assertEqual(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag1.id, self.tag2.id,
                               self.tag1.id + self.tag2.id)
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tags_by_name(self):
        self.assertEqual(self.tagset.count(), 3)
        self.tagset.remove(self.tag0.name, self.tag2.name)
        self.assertEqual(self.tagset.count(), 1)
        self.assertNotIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertNotIn(self.tag2, self.tagset)

    def test_remove_several_tags_incl_nonexisting_by_name_ERROR(self):
        self.assertEqual(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag0.name, self.tag2.name, 'foooo')
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tags(self):
        self.assertEqual(self.tagset.count(), 3)
        self.tagset.remove(self.tag0, self.tag1.id, self.tag2.name)
        self.assertFalse(self.tagset.exists())

    def test_remove_several_tags_incl_nonexisting_ID_ERROR(self):
        self.assertEqual(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag0, self.tag1.id, self.tag2.name, 5)
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_several_tags_incl_nonexisting_name_ERROR(self):
        self.assertEqual(self.tagset.count(), 3)
        with self.assertRaises(NoSuchTagError):
            self.tagset.remove(self.tag0, self.tag1.id, self.tag2.name, 'fooo')
        self.assertEqual(self.tagset.count(), 3)
        self.assertIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_same_tag_thrice_simultaneously(self):
        self.assertEqual(self.tagset.count(), 3)
        self.tagset.remove(self.tag0, self.tag0.id, self.tag0.name)
        self.assertEqual(self.tagset.count(), 2)
        self.assertNotIn(self.tag0, self.tagset)
        self.assertIn(self.tag1, self.tagset)
        self.assertIn(self.tag2, self.tagset)

    def test_remove_same_tag_thrice_simultaneously(self):
        self.assertEqual(self.tagset.count(), 3)
        self.tagset.remove(self.tag0)
        self.tagset.remove(self.tag0.id)
        self.tagset.remove(self.tag0.name)
        self.assertEqual(self.tagset.count(), 2)
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
        self.supertag._inclusions.add(self.subtag0)


class TagInclusionTests(InclusionSetupMixin, TestCase):
    """
    Test for Tag model's inclusion mechanism
    """

    def test_inclusion_relation(self):
        self.assertEqual(self.supertag._inclusions.count(), 1)
        self.assertEqual(self.subtag0._inclusions.count(), 0)
        self.assertEqual(self.subtag1._inclusions.count(), 0)
        self.assertTrue(self.supertag._inclusions.filter(id=self.subtag0.id).exists())
        self.assertFalse(self.subtag0._inclusions.filter(id=self.supertag.id).exists())

    def test_include_method_with_tag_id(self):
        self.assertEqual(self.supertag._inclusions.count(), 1)
        self.assertEqual(self.subtag1._inclusions.count(), 0)
        self.supertag.include(self.subtag1.id)
        self.assertEqual(self.supertag._inclusions.count(), 2)
        self.assertEqual(self.subtag1._inclusions.count(), 0)
        self.assertTrue(self.supertag._inclusions.filter(id=self.subtag1.id).exists())
        self.assertFalse(self.subtag1._inclusions.filter(id=self.supertag.id).exists())

    def test_include_method_with_tag_instance(self):
        self.assertEqual(self.supertag._inclusions.count(), 1)
        self.assertEqual(self.subtag1._inclusions.count(), 0)
        self.supertag.include(self.subtag1)
        self.assertEqual(self.supertag._inclusions.count(), 2)
        self.assertEqual(self.subtag1._inclusions.count(), 0)
        self.assertTrue(self.supertag._inclusions.filter(id=self.subtag1.id).exists())
        self.assertFalse(self.subtag1._inclusions.filter(id=self.supertag.id).exists())

    def test_include_method_with_tag_name(self):
        self.assertEqual(self.supertag._inclusions.count(), 1)
        self.assertEqual(self.subtag1._inclusions.count(), 0)
        self.supertag.include(self.subtag1.name)
        self.assertEqual(self.supertag._inclusions.count(), 2)
        self.assertEqual(self.subtag1._inclusions.count(), 0)
        self.assertTrue(self.supertag._inclusions.filter(id=self.subtag1.id).exists())
        self.assertFalse(self.subtag1._inclusions.filter(id=self.supertag.id).exists())

    def test_uninclude_method_with_tag_id(self):
        self.assertIn(self.subtag0, self.supertag._inclusions.all())
        self.supertag.uninclude(self.subtag0.id)
        self.assertNotIn(self.subtag0, self.supertag._inclusions.all())

    def test_uninclude_method_with_tag_instance(self):
        self.assertIn(self.subtag0, self.supertag._inclusions.all())
        self.supertag.uninclude(self.subtag0)
        self.assertNotIn(self.subtag0, self.supertag._inclusions.all())

    def test_uninclude_method_with_tag_name(self):
        self.assertIn(self.subtag0, self.supertag._inclusions.all())
        self.supertag.uninclude(self.subtag0.name)
        self.assertNotIn(self.subtag0, self.supertag._inclusions.all())

    def test_uninclude_not_included_does_nothing(self):
        self.assertIn(self.subtag0, self.supertag._inclusions.all())
        self.assertNotIn(self.subtag1, self.supertag._inclusions.all())
        self.assertEqual(self.supertag._inclusions.count(), 1)
        self.supertag.uninclude(self.subtag1)
        self.assertIn(self.subtag0, self.supertag._inclusions.all())
        self.assertNotIn(self.subtag1, self.supertag._inclusions.all())
        self.assertEqual(self.supertag._inclusions.count(), 1)

    def test_self_inclusion_does_nothing(self):
        """
        A tag including itself, while not an error, is rather meaningless.

        Attempting to do that should just have no effect at all.
        """
        self.assertEqual(self.subtag1._inclusions.count(), 0)
        self.subtag1.include(self.subtag1)
        self.assertEqual(self.subtag1._inclusions.count(), 0)
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
        self.assertTrue(self.supertag.includes(self.subtag0.id))
        self.assertFalse(self.supertag.includes(self.subtag1.id))
        self.assertFalse(self.subtag0.includes(self.supertag.id))
        self.assertFalse(self.subtag1.includes(self.supertag.id))

    def test_includes_method_with_tag_instances(self):
        self.assertTrue(self.supertag.includes(self.subtag0))
        self.assertFalse(self.supertag.includes(self.subtag1))
        self.assertFalse(self.subtag0.includes(self.supertag))
        self.assertFalse(self.subtag1.includes(self.supertag))

    def test_includes_method_with_tag_names(self):
        self.assertTrue(self.supertag.includes(self.subtag0.name))
        self.assertFalse(self.supertag.includes(self.subtag1.name))
        self.assertFalse(self.subtag0.includes(self.supertag.name))
        self.assertFalse(self.subtag1.includes(self.supertag.name))


class TagSetInclusionTests(InclusionSetupMixin, TestCase):
    """
    Tests for TagSet model's handling of tag inclusions
    """

    def setUp(self):
        super(TagSetInclusionTests, self).setUp()
        self.tagset = TagSet.objects.create()

    def test_adding_tag_that_is_included_by_other_tag_adds_both(self):
        self.assertEqual(self.tagset.count(), 0)
        self.tagset.add(self.subtag0)
        self.assertTrue(self.subtag0 in self.tagset)
        self.assertEqual(self.tagset.count(), 2)
        self.assertTrue(self.supertag in self.tagset)


class FixtureSetupMixin(object):
    """
    Mixin to provide common setUp method for fixture-based test classes
    """

    def setUp(self):
        self.tagset = TagSet.objects.create()
        self.django = Tag.objects.get(name='Django')
        self.javascript = Tag.objects.get(name='JavaScript')
        self.knowledge_management = Tag.objects.get(name='Knowledge Management')
        self.programming = Tag.objects.get(name='Programming')
        self.python = Tag.objects.get(name='Python')
        self.tagging = Tag.objects.get(name='Tagging')
        self.taggsonomy = Tag.objects.get(name='Taggsonomy')
        self.web_development = Tag.objects.get(name='Web Development')


class BasicInclusionTests(FixtureSetupMixin, TestCase):
    """
    Tests for various inclusion scenarios
    """
    fixtures = ['tags.json']

    def test_adding_tag_with_subtag_to_tagset_also_adds_subtag(self):
        self.tagset.add(self.tagging)
        self.assertIn(self.knowledge_management, self.tagset)

    def test_adding_tag_with_sub_and_supertag_to_tagset_adds_subtag_not_supertag(self):
        self.tagset.add(self.python)
        self.assertIn(self.programming, self.tagset)
        self.assertNotIn(self.django, self.tagset)
        
    def test_adding_tag_with_two_subtags_to_tagset_adds_both_subtags(self):
        self.tagset.add(self.javascript)
        self.assertIn(self.programming, self.tagset)
        self.assertIn(self.web_development, self.tagset)

    def test_adding_tag_subsubtag_to_tagset_adds_subtag_and_subsubtag(self):
        self.tagset.add(self.django)
        self.assertIn(self.python, self.tagset)
        self.assertIn(self.programming, self.tagset)
        

class BasicExclusionTests(FixtureSetupMixin, TestCase):
    """
    Tests for various exclusion scenarios
    """
    fixtures = ['tags.json', 'tagsets.json']

    def test_adding_tag_excluding_other_tag_to_tagset_removes_other_tag(self):
        # Get the TagSet that already contains the Tag "Knowledge Management"
        # (and nothing else)
        tagset = TagSet.objects.get(pk=1)
        self.assertIn(self.knowledge_management, tagset)
        tagset.add(self.programming)
        self.assertNotIn(self.knowledge_management, tagset)

    def test_excluding_tags_that_are_already_jointly_present_in_tagset_ERROR(self):
        # Get the TagSet that already contains the Tags "Tagging" AND "Taggsonomy"
        tagset = TagSet.objects.get(pk=2)
        self.assertIn(self.tagging, tagset)
        self.assertIn(self.taggsonomy, tagset)
        with self.assertRaises(MutualExclusionError):
            self.tagging.exclude(self.taggsonomy)
        with self.assertRaises(MutualExclusionError):
            self.taggsonomy.exclude(self.tagging)


class NewInclusionRelationTests(FixtureSetupMixin, TestCase):
    """
    Tests for various scenarios involving the adding of new inclusion relations
    """
    fixtures = ['tags.json', 'tagsets.json']

    def test_circular_inclusion_ERROR(self):
        with self.assertRaises(CircularInclusionError):
            self.django.include(Tag.objects.get(name='Programming'))

    def test_new_inclusion_does_not_add_supertag_by_default(self):
        # Get the TagSet that already contains the Tag "Django" (and nothing else)
        tagset = TagSet.objects.get(pk=3)
        self.assertNotIn(self.web_development, tagset)
        self.web_development.include(self.django)
        self.assertNotIn(self.web_development, tagset)

    def test_new_inclusion_does_not_add_supertag_when_update_disabled(self):
        # Get the TagSet that already contains the Tag "Django" (and nothing else)
        tagset = TagSet.objects.get(pk=3)
        self.assertNotIn(self.web_development, tagset)
        self.web_development.include(self.django, update_tagsets=False)
        self.assertNotIn(self.web_development, tagset)

    def test_new_inclusion_adds_supertag_when_update_enabled(self):
        # Get the TagSet that already contains the Tag "Django" (and nothing else)
        tagset = TagSet.objects.get(pk=3)
        self.assertNotIn(self.web_development, tagset)
        self.web_development.include(self.django, update_tagsets=True)
        self.assertIn(self.web_development, tagset)

    def test_new_inclusion_adds_all_supertags_when_update_enabled(self):
        # Get the TagSet that already contains the Tag "Taggsonomy"
        tagset = TagSet.objects.get(pk=4)
        self.assertNotIn(self.tagging, tagset)
        self.assertNotIn(self.knowledge_management, tagset)
        self.tagging.include(self.taggsonomy, update_tagsets=True)
        self.assertIn(self.tagging, tagset)
        self.assertIn(self.knowledge_management, tagset)

    def test_new_inclusion_does_not_add_unrelated_supertags_when_update_enabled(self):
        # Get the TagSet that already contains the Tag "Django" (and nothing else)
        tagset = TagSet.objects.get(pk=3)
        self.assertIn(self.django, tagset)
        self.assertNotIn(self.python, tagset)
        self.assertNotIn(self.programming, tagset)
        self.web_development.include(self.django, update_tagsets=True)
        self.assertIn(self.django, tagset)
        self.assertNotIn(self.python, tagset)
        self.assertNotIn(self.programming, tagset)

    def test_new_inclusion_disallows_exclusion(self):
        self.web_development.include(self.django)
        with self.assertRaises(CommonSubtagExclusionError):
            self.programming.exclude(self.web_development)
        with self.assertRaises(CommonSubtagExclusionError):
            self.web_development.exclude(self.programming)

    def test_new_inclusion_does_not_touch_tagsets_without_update_enabled(self):
        # Create a TagSet and add the Tags "Programming" and "Taggsonomy"
        tagset = TagSet.objects.create()
        tagset.add(self.taggsonomy, self.programming)
        self.tagging.include(self.taggsonomy)
        self.assertIn(self.programming, tagset)
        self.assertNotIn(self.tagging, tagset)

    def test_new_inclusion_which_would_lead_to_silent_removal_of_tags_ERROR(self):
        # Create a TagSet and add the Tags "Programming" and "Taggsonomy"
        tagset = TagSet.objects.create()
        tagset.add(self.taggsonomy, self.programming)
        with self.assertRaises(SupertagAdditionWouldRemoveExcludedError):
            self.tagging.include(self.taggsonomy, update_tagsets=True)
        self.assertIn(self.programming, tagset)

    def test_new_inclusion_for_mutually_exclusive_supertags_ERROR(self):
        self.tagging.include(self.taggsonomy)
        self.assertTrue(self.tagging.includes(self.taggsonomy))
        self.assertTrue(self.knowledge_management.includes(self.taggsonomy))
        with self.assertRaises(MutuallyExclusiveSupertagsError):
            self.python.include(self.taggsonomy)
        with self.assertRaises(MutuallyExclusiveSupertagsError):
            self.django.include(self.taggsonomy)

    def test_new_inclusion_succeeds_after_unexcluding_supertags(self):
        self.tagging.include(self.taggsonomy)
        self.programming.unexclude(self.knowledge_management)
        self.python.include(self.taggsonomy)
        self.assertTrue(self.python.includes(self.taggsonomy))
        self.assertTrue(self.tagging.includes(self.taggsonomy))
        self.assertTrue(self.programming.includes(self.taggsonomy))
        self.assertTrue(self.knowledge_management.includes(self.taggsonomy))

    def test_new_inclusion_disallows_excluding_supertags_ERROR(self):
        self.tagging.include(self.taggsonomy)
        self.programming.unexclude(self.knowledge_management)
        self.python.include(self.taggsonomy)
        with self.assertRaises(CommonSubtagExclusionError):
            self.programming.exclude(self.knowledge_management)
        with self.assertRaises(CommonSubtagExclusionError):
            self.knowledge_management.exclude(self.programming)


class SupertagTests(FixtureSetupMixin, TestCase):
    """
    Tests for handling of supertags by tags
    """
    fixtures = ['tags.json']

    def test_get_all_supertags_vertical(self):
        django_supertags = self.django.get_all_supertags()
        self.assertIn(self.python, django_supertags)
        self.assertIn(self.programming, django_supertags)
        self.assertNotIn(self.web_development, django_supertags)

    def test_get_all_supertags_horizontal(self):
        js_supertags = self.javascript.get_all_supertags()
        self.assertIn(self.programming, js_supertags)
        self.assertIn(self.web_development, js_supertags)
        self.assertNotIn(self.python, js_supertags)

    def test_get_direct_supertags_vertical(self):
        django_supertags = self.django.get_direct_supertags()
        self.assertIn(self.python, django_supertags)
        self.assertNotIn(self.programming, django_supertags)
        self.assertNotIn(self.web_development, django_supertags)

    def test_get_direct_supertags_horizontal(self):
        js_supertags = self.javascript.get_direct_supertags()
        self.assertIn(self.programming, js_supertags)
        self.assertIn(self.web_development, js_supertags)
        self.assertNotIn(self.python, js_supertags)

    def test_get_indirect_supertags_vertical(self):
        django_supertags = self.django.get_indirect_supertags()
        self.assertNotIn(self.python, django_supertags)
        self.assertIn(self.programming, django_supertags)
        self.assertNotIn(self.web_development, django_supertags)

    def test_get_indirect_supertags_horizontal(self):
        js_supertags = self.javascript.get_indirect_supertags()
        self.assertFalse(js_supertags.exists())


class SubtagTests(FixtureSetupMixin, TestCase):
    """
    Tests for handling of subtags by tags
    """
    fixtures = ['tags.json']

    def test_get_all_subtags_simple(self):
        all_subtags = self.knowledge_management.get_all_subtags()
        self.assertEqual(all_subtags.count(), 1)
        self.assertIn(self.tagging, all_subtags)

    def test_get_all_subtags_complex(self):
        all_subtags = self.programming.get_all_subtags()
        self.assertEqual(all_subtags.count(), 3)
        self.assertIn(self.django, all_subtags)
        self.assertIn(self.python, all_subtags)
        self.assertIn(self.javascript, all_subtags)

    def test_get_direct_subtags(self):
        direct_subtags = self.programming.get_direct_subtags()
        self.assertEqual(direct_subtags.count(), 2)
        self.assertIn(self.python, direct_subtags)
        self.assertIn(self.javascript, direct_subtags)
        self.assertNotIn(self.django, direct_subtags)

    def test_get_indirect_subtags(self):
        indirect_subtags = self.programming.get_indirect_subtags()
        self.assertEqual(indirect_subtags.count(), 1)
        self.assertIn(self.django, indirect_subtags)
        self.assertNotIn(self.python, indirect_subtags)
        self.assertNotIn(self.javascript, indirect_subtags)
