from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse_lazy
from django.views import generic

from .models import Tag, TagSet


class TagDetailView(generic.DetailView):
    fields = {'name'}
    model = Tag


class TagListView(generic.ListView):
    model = Tag


def add_tags(request, tagset_id):
    name_string = request.POST.get('tag_names')
    names = [ name.strip() for name in name_string.split(',')]
    TagSet.objects.get(id=tagset_id).add(*names, create_nonexisting=True)
    try:
        return redirect(request.META.get('HTTP_REFERER'))
    except NoReverseMatch:
        return redirect('/')

def remove_tag(request, tagset_id, tag_id):
    TagSet.objects.get(id=tagset_id).remove(tag_id)
    try:
        return redirect(request.META.get('HTTP_REFERER'))
    except NoReverseMatch:
        return redirect('/')
