from django.apps import AppConfig


class TaggsonomyConfig(AppConfig):
    name = 'taggsonomy'

    def ready(self):
        # register signals
        from . import signals
