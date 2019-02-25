from django import template
from django.contrib.contenttypes.models import ContentType

from taggsonomy.models import TagSet


def get_tagset_for_object(object_):
    content_type = ContentType.objects.get_for_model(object_)
    tagset, _ = TagSet.objects.get_or_create(content_type=content_type,
                                             object_id=object_.id)
    return tagset

register = template.Library()

@register.inclusion_tag('taggsonomy/tags.html')
def tags(tagged_object):
    tagset = get_tagset_for_object(tagged_object)
    return {'tags' :  tagset.all()}

@register.inclusion_tag('taggsonomy/active_tags.html')
def active_tags(tagged_object):
    tagset = get_tagset_for_object(tagged_object)
    return {'tagset' :  tagset}
