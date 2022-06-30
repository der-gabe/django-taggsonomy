from django.test import TestCase

from django_taggsonomy.errors import (
    MutualExclusionError, SelfExclusionError,
    SimultaneousInclusionExclusionError)
from django_taggsonomy.models import TagSet

from .mixins import ExclusionSetupMixin, InclusionSetupMixin, FixtureSetupMixin


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
