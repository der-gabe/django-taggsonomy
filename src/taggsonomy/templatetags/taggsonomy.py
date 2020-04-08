from django import template
from django.urls import reverse

from taggsonomy.models import Tag, TagSet
from taggsonomy.models.base import ExclusionTagSet, SuperTagSet, SubTagSet
from taggsonomy.utils import get_tag_object, get_or_create_tagset_for_object


register = template.Library()

@register.inclusion_tag('taggsonomy/tag.html')
def tag(tag, removable_from=None, url=''):
    """
    Templatetag to render a single tag

    :param tag: The tag to render
    :type tag: Tag, str or int
    :param removable_from: The context from which the tag may be removed,
                           e.g. a TagSet or tagged/taggable object instance.
    :type removable_from: object, optional
    :param url: An (optionally formattable) string to serve as the tag's target URL
    :type url: str, optional
    """
    template_context = {'tag': get_tag_object(tag)}
    if isinstance(removable_from, TagSet):
        template_context.update({'removal_url': reverse('taggsonomy:remove-tag', args=(removable_from.id, tag.id))})
    elif isinstance(removable_from, ExclusionTagSet):
        template_context.update({'removal_url': reverse('taggsonomy:unexclude-tag', args=(removable_from.tag.id, tag.id))})
    elif isinstance(removable_from, SuperTagSet):
        template_context.update({'removal_url': reverse('taggsonomy:remove-supertag', args=(removable_from.tag.id, tag.id))})
    elif isinstance(removable_from, SubTagSet):
        template_context.update({'removal_url': reverse('taggsonomy:remove-subtag', args=(removable_from.tag.id, tag.id))})
    if url:
        template_context.update({'url': url.format(tag=tag)})
    return template_context

@register.inclusion_tag('taggsonomy/tags.html')
def tags(tagged_object, url=''):
    tagset = get_or_create_tagset_for_object(tagged_object)
    return {'tags' :  tagset.all(), 'url': url}

@register.inclusion_tag('taggsonomy/active_tags.html')
def active_tags(tagged_object, url=''):
    tagset = get_or_create_tagset_for_object(tagged_object)
    return {'tagset' :  tagset, 'url': url}

@register.inclusion_tag('taggsonomy/add_tags.html')
def add_tags_form(tagged_object):
    tagset = get_or_create_tagset_for_object(tagged_object)
    contained_ids = [ tag.id for tag in tagset.all() ]
    tags = Tag.objects.exclude(id__in=contained_ids)
    return {'tags': tags, 'tagset' :  tagset}

@register.inclusion_tag('taggsonomy/tag_manager.html')
def tag_manager(tagged_object, url=''):
    return {'object': tagged_object, 'url': url}
