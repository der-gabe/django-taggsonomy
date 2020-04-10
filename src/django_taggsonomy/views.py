from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse_lazy
from django.views import generic

from .forms import TagForm
from .models import Tag, TagSet


class TagCreateView(generic.CreateView):
    template_name = 'taggsonomy/tag_create_form.html'
    form_class = TagForm
    model = Tag


class TagDeleteView(generic.DeleteView):
    template_name = 'taggsonomy/tag_confirm_delete.html'
    model = Tag
    success_url = reverse_lazy('taggsonomy:tag-list')


class TagEditView(generic.UpdateView):
    template_name = 'taggsonomy/tag_edit_form.html'
    form_class = TagForm
    model = Tag


class TagListView(generic.ListView):
    template_name = 'taggsonomy/tag_list.html'
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


def remove_subtag(request, tag_id, subtag_id):
    Tag.objects.get(id=tag_id).uninclude(subtag_id)
    try:
        return redirect(request.META.get('HTTP_REFERER'))
    except NoReverseMatch:
        return redirect('/')


def remove_supertag(request, tag_id, supertag_id):
    Tag.objects.get(id=supertag_id).uninclude(tag_id)
    try:
        return redirect(request.META.get('HTTP_REFERER'))
    except NoReverseMatch:
        return redirect('/')


def unexclude_tag(request, tag_id, excluded_tag_id):
    Tag.objects.get(id=tag_id).unexclude(excluded_tag_id)
    try:
        return redirect(request.META.get('HTTP_REFERER'))
    except NoReverseMatch:
        return redirect('/')
