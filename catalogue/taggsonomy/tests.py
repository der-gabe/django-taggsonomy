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

    def test_add_single_tag_instance(self):
        self.tagset.add(self.tag0)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 1)
        self.assertIn(self.tag0, self.tagset().all())

    def test_add_single_tag_by_ID(self):
        self.tagset.add(self.tag0.id)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 1)
        self.assertIn(self.tag0, self.tagset().all())

    def test_add_single_existing_tag_by_name(self):
        self.tagset.add(self.tag0.name)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 1)
        self.assertIn(self.tag0, self.tagset().all())

    def test_add_single_nonexisting_tag_by_name(self):
        self.tagset.add('foooo')
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 1)
        self.assertTrue(self.tagset().filter(name='foooo').exists())
        self.assertEquals(self.tagset().filter(name='foooo').count(), 1)

    def test_add_single_nonexisting_tag_by_name_ERROR(self):
        with self.assertRaises(NoSuchTagError):
            self.tagset.add('foooo', only_existing=True)
        self.assertFalse(self.tagset().exists())

    def test_add_several_tag_instances(self):
        self.tagset.add(self.tag0, self.tag1, self.tag2)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 3)
        self.assertIn(self.tag0, self.tagset().all())
        self.assertIn(self.tag1, self.tagset().all())
        self.assertIn(self.tag2, self.tagset().all())

    def test_add_several_tags_by_ID(self):
        self.tagset.add(self.tag0.id, self.tag1.id, self.tag2.id)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 3)
        self.assertIn(self.tag0, self.tagset().all())
        self.assertIn(self.tag1, self.tagset().all())
        self.assertIn(self.tag2, self.tagset().all())

    def test_add_several_existing_tags_by_name(self):
        self.tagset.add(self.tag0.name, self.tag1.name, self.tag2.name)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 3)
        self.assertIn(self.tag0, self.tagset().all())
        self.assertIn(self.tag1, self.tagset().all())
        self.assertIn(self.tag2, self.tagset().all())

    def test_add_several_nonexisting_tags_by_name(self):
        self.tagset.add('foooo', 'baaar', 'baaaz')
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 3)
        self.assertEquals(self.tagset().filter(name='foooo').count(), 1)
        self.assertEquals(self.tagset().filter(name='baaar').count(), 1)
        self.assertEquals(self.tagset().filter(name='baaaz').count(), 1)

    def test_add_several_nonexisting_tags_by_name_ERROR(self):
        """
        Test attempt to add non-existing tags by name when `only_existing=True`

        Should not add any tags and instead raise `NoSuchTagError`
        """
        with self.assertRaises(NoSuchTagError):        
            self.tagset.add('foooo', 'baaar', 'baaaz', only_existing=True)
        self.assertFalse(self.tagset().exists())

    def test_add_several_tags_by_name(self):
        """
        Test addition of existing and non-existing tags by name
        """
        self.tagset.add(
            self.tag0.name, self.tag1.name, self.tag2.name,
            'foooo', 'baaar', 'baaaz'
        )
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 6)
        self.assertIn(self.tag0, self.tagset().all())
        self.assertIn(self.tag1, self.tagset().all())
        self.assertIn(self.tag2, self.tagset().all())
        self.assertTrue(self.tagset()
                            .filter(name__in=['foooo', 'baaar', 'baaaz'])
                            .exists())
        self.assertEquals(self.tagset().filter(name='foooo').count(), 1)
        self.assertEquals(self.tagset().filter(name='baaar').count(), 1)
        self.assertEquals(self.tagset().filter(name='baaaz').count(), 1)

    def test_add_several_tags_by_name_ERROR(self):
        """
        Test attempt to add existing and non-existing tags by name when
        `only_existing=True`

        Should not add any tags and instead raise `NoSuchTagError`
        """
        with self.assertRaises(NoSuchTagError):        
            self.tagset.add(
                self.tag0.name, self.tag1.name, self.tag2.name,
                'foooo', 'baaar', 'baaaz', only_existing=True
            )
        self.assertFalse(self.tagset().exists())

    def test_add_several_tags(self):
        """
        Test addition of several tags at once by different types:
        - Tag (instance),
        - int (ID) and
        - str (name),
        including a non-existing tag by name (str)
        """
        self.tagset.add(self.tag0, self.tag1.id, self.tag2.name, 'foooo')
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 4)
        self.assertIn(self.tag0, self.tagset().all())
        self.assertIn(self.tag1, self.tagset().all())
        self.assertIn(self.tag2, self.tagset().all())
        self.assertTrue(self.tagset().filter(name='foooo').exists())
        self.assertEquals(self.tagset().filter(name='foooo').count(), 1)

    def test_add_several_tags_ERROR(self):
        """
        Test attempt to add several tags at once by different types:
        - Tag (instance),
        - int (ID) and
        - str (name),
        including a non-existing tag by name (str) with `only_existing=True`

        Should not add any tags and instead raise `NoSuchTagError`
        """
        with self.assertRaises(NoSuchTagError):        
            self.tagset.add(self.tag0, self.tag1.id, self.tag2.name, 'foooo',
                            only_existing=True)
        self.assertFalse(self.tagset().exists())

    def test_add_same_tag_twice_simultaneously_by_instance(self):
        self.tagset.add(self.tag0, self.tag0)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 1)
        self.assertIn(self.tag0, self.tagset().all())

    def test_add_same_tag_thrice_simultaneously(self):
        self.tagset.add(self.tag0, self.tag0.id, self.tag0.name)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 1)
        self.assertIn(self.tag0, self.tagset().all())        

    def test_add_same_tag_thrice_sequentially(self):
        self.tagset.add(self.tag0)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 1)
        self.assertIn(self.tag0, self.tagset().all())        

        self.tagset.add(self.tag0.id)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 1)
        self.assertIn(self.tag0, self.tagset().all())        

        self.tagset.add(self.tag0.name)
        self.assertTrue(self.tagset().exists())
        self.assertEquals(self.tagset().count(), 1)
        self.assertIn(self.tag0, self.tagset().all())        
