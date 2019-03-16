from django.contrib.contenttypes.models import ContentType

from .models import TagSet


def get_tagset_for_object(object_):
    content_type = ContentType.objects.get_for_model(object_)
    try:
        tagset = TagSet.objects.get(content_type=content_type,
                                    object_id=object_.id)
    except TagSet.DoesNotExist:
        tagset = None
    return tagset

def get_or_create_tagset_for_object(object_):
    content_type = ContentType.objects.get_for_model(object_)
    tagset, _ = TagSet.objects.get_or_create(content_type=content_type,
                                             object_id=object_.id)
    return tagset
