from django.apps import AppConfig


class TaggsonomyConfig(AppConfig):
    name = 'django_taggsonomy'

    def ready(self):
        # register signals
        from . import signals
