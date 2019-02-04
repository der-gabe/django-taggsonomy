from django import template
from django.contrib.contenttypes.models import ContentType

from taggsonomy.models import TagSet


register = template.Library()

@register.simple_tag
def tags(tagged_object):
    tagset, _ = TagSet.objects.get_or_create(content_type=ContentType.objects.get_for_model(tagged_object), object_id=tagged_object.id)
    return 'Tags: ' + ', '.join([str(tag) for tag in tagset.all()]) if tagset.exists() else ''
