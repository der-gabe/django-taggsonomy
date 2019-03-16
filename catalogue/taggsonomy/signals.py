from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import TagSet
from .utils import get_or_create_tagset_for_object


@receiver(pre_delete)
def delete_tagset(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance:
        content_type = ContentType.objects.get_for_model(instance)
        if TagSet.objects\
                 .filter(content_type=content_type,
                         object_id=instance.id)\
                 .exists():
            tagset = get_or_create_tagset_for_object(instance)
            tagset.delete()
