from django.contrib.contenttypes.models import ContentType

from .errors import TagTypeError
from .models import Tag, TagSet


def get_tag_object(tag):
    """
    Return the corresponding Tag object instance for a given:
    - instance (i.e. passthrough, NO-OP)
    - name (str)
    - object ID (int)

    Raises:
    - Tag.DoesNotExist (if there's not tag with the given name or ID)
    - TagTypeError if the type of `tag` is not one of the expected types.
    """
    if isinstance(tag, Tag):
        return tag
    elif isinstance(tag, str):
        return Tag.objects.get(name=tag)
    elif isinstance(tag, int):
        return Tag.objects.get(id=tag)
    else:
        raise TagTypeError

def get_tagset_for_object(object_):
    content_type = ContentType.objects.get_for_model(object_)
    try:
        tagset = TagSet.objects.get(content_type=content_type,
                                    object_id=object_.id)
    except (AttributeError, TagSet.DoesNotExist):
        tagset = None
    return tagset

def get_or_create_tagset_for_object(object_):
    content_type = ContentType.objects.get_for_model(object_)
    tagset, _ = TagSet.objects.get_or_create(content_type=content_type,
                                             object_id=object_.id)
    return tagset
