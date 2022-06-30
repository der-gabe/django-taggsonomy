from django.test import TestCase

from django_taggsonomy.errors import (
    CircularInclusionError, CommonSubtagExclusionError, MutualExclusionError,
    MutuallyExclusiveSupertagsError, NoSuchTagError,
    SupertagAdditionWouldRemoveExcludedError)
from django_taggsonomy.models import Tag, TagSet

from .mixins import ExclusionSetupMixin, InclusionSetupMixin, FixtureSetupMixin


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

    def test_adding_tags_with_excluded_supertags_ERROR(self):
        subtag = Tag.objects.create(name='barbar')
        self.tag1.include(subtag)
        with self.assertRaises(MutuallyExclusiveSupertagsError):
            self.tagset.add(self.tag0, subtag)
        self.assertFalse(self.tagset.exists())

    def test_adding_tags_with_mutually_exclusive_supertags_ERROR(self):
        subtag0 = Tag.objects.create(name='foofoo')
        self.tag0.include(subtag0)
        subtag1 = Tag.objects.create(name='barbar')
        self.tag1.include(subtag1)
        with self.assertRaises(MutuallyExclusiveSupertagsError):
            self.tagset.add(subtag0, subtag1)
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
