from django.contrib.contenttypes.models import ContentType

from taggsonomy.models import Tag, TagSet


def get_tagset_for_object(object_):
    content_type = ContentType.objects.get_for_model(object_)
    tagset, _ = TagSet.objects.get_or_create(content_type=content_type,
                                             object_id=object_.id)
    return tagset
