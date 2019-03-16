from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import TagSet
from .utils import (get_tagset_for_object,
                    get_or_create_tagset_for_object)


@receiver(pre_delete)
def delete_tagset(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance:
        content_type = ContentType.objects.get_for_model(instance)
        tagset = get_tagset_for_object(instance)
        if tagset:
            tagset.delete()
