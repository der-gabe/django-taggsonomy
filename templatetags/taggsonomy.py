from django import template
from django.urls import reverse

from taggsonomy.models import Tag, TagSet
from taggsonomy.utils import get_tag_object, get_or_create_tagset_for_object


register = template.Library()

@register.inclusion_tag('taggsonomy/tag.html')
def tag(tag, tag_context=None, removable=False, url=''):
    """
    Templatetag to render a single tag

    :param tag: The tag to render
    :type tag: Tag, str or int
    :param tag_context: The context (object) from which to remove the tag, e.g. a TagSet.
                        Only relevant iff removable=True - then it's needed to determine the removal URL
    :type tag_context: TagSet, optional
    :param removable: `True` if the tag should be rendered with a little 'x', hyperlinked to a removal URL
    :type removable: bool, optional
    :param url: An (optionally formattable) string to serve as the tag's target URL
    :type url: str, optional
    """
    template_context = {'tag': get_tag_object(tag)}
    if removable and tag_context:
        if isinstance(tag_context, TagSet):
            tagset = tag_context
            template_context.update({'removal_url': reverse('taggsonomy:remove-tag', args=(tagset.id, tag.id))})
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
