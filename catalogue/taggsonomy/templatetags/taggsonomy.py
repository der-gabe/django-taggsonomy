from django import template

from taggsonomy.models import Tag
from taggsonomy.utils import get_or_create_tagset_for_object


register = template.Library()

@register.inclusion_tag('taggsonomy/tags.html')
def tags(tagged_object):
    tagset = get_or_create_tagset_for_object(tagged_object)
    return {'tags' :  tagset.all()}

@register.inclusion_tag('taggsonomy/active_tags.html')
def active_tags(tagged_object):
    tagset = get_or_create_tagset_for_object(tagged_object)
    return {'tagset' :  tagset}

@register.inclusion_tag('taggsonomy/add_tags.html')
def add_tags_form(tagged_object):
    tagset = get_or_create_tagset_for_object(tagged_object)
    contained_ids = [ tag.id for tag in tagset.all() ]
    tags = Tag.objects.exclude(id__in=contained_ids)
    return {'tags': tags, 'tagset' :  tagset}
