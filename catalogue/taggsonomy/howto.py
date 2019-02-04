from django.contrib.contenttypes.models import ContentType
from files.models import File
from taggsonomy.models import Tag, TagSet

file1 = File.objects.first()
# <File: openSUSE-Leap-15.0-DVD-x86_64.iso.sha256 (630 bytes)>
TagSet.objects.create(content_object=file1)
# <TagSet: TagSet object (3)>
file1_tags = TagSet.objects.get(content_type=ContentType.objects.get_for_model(file1), object_id=file1.id)
# file1_tags:
# <TagSet: TagSet object (3)>

file1_tags.all()
# <QuerySet []>
file1_tags.add('SUSE', 'openSUSE')
file1_tags.all()
# <QuerySet [<Tag: openSUSE>, <Tag: SUSE>]>
