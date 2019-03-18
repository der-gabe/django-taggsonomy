from django.test import TestCase

from .errors import NoSuchTagError
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
        Test attempt to add non-existing tags by name when `create_nonexisting=False`, which is the default

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
        including a non-existing tag by name (str) with `create_nonexisting=False`, which is the default

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


class TagExclusionTests(TestCase):
    """
    Tests for Tag model's exclusion mechanism
    """

    def setUp(self):
        self.tag0 = Tag.objects.create(name='foo')
        self.tag1 = Tag.objects.create(name='bar')
        self.tag2 = Tag.objects.create(name='baz')
        # Let tag0 exclude both other tags: tag1 *and* tag2
        self.tag0._exclusions.add(self.tag1, self.tag2)
        # Note that this does *not* mean that tag1 excludes tag2, or vice versa

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

    def test_exclude_tag_instance(self):
        self.tag1.exclude(self.tag2)
        self.assertTrue(self.tag1._exclusions.filter(id=self.tag2.id).exists())
        self.assertTrue(self.tag2._exclusions.filter(id=self.tag1.id).exists())


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
