from django_taggsonomy.models import Tag, TagSet

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


class InclusionSetupMixin(object):
    """
    Mixin to provide common setUp method for inclusion test cases
    """

    def setUp(self):
        self.supertag = Tag.objects.create(name='Programming')
        self.subtag0 = Tag.objects.create(name='Python')
        self.subtag1 = Tag.objects.create(name='JavaScript')
        self.supertag._inclusions.add(self.subtag0)


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
