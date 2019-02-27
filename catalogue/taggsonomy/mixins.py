from .utils import get_tagset_for_object

class TaggableMixin(object):
    """
    Mixin to provide model classes with a `tags` property to access the model's associated TagSet
    """

    @property
    def tags(self):
        """
        Return the TagSet associated with this model instance.

        This will *create* a Tagset for this object
        if one doesn't exist already.
        """
        return get_tagset_for_object(self)
