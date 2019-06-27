from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse_lazy
from django.views import generic

from .forms import TagForm
from .models import Tag, TagSet


class TagCreateView(generic.CreateView):
    template_name_suffix = '_create_form'
    form_class = TagForm
    model = Tag

class TagDeleteView(generic.DeleteView):
    model = Tag
    success_url = reverse_lazy('taggsonomy:tag-list')

class TagEditView(generic.UpdateView):
    template_name_suffix = '_edit_form'
    form_class = TagForm
    model = Tag

    def form_valid(self, form):
        self.object.color = self.request.POST.get('color').lstrip('#')
        return super(TagEditView, self).form_valid(form)


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
