from django.urls import NoReverseMatch
from django.shortcuts import redirect

from .models import Tag, TagSet


def remove_tag_from(request, tag_id, tagset_id):
    TagSet.objects.get(id=tagset_id).remove(tag_id)
    try:
        return redirect(request.META.get('HTTP_REFERER'))
    except NoReverseMatch:
        return redirect('/')
