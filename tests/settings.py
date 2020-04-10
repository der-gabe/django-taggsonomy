DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        }
}
FIXTURE_DIRS = (
    'tests/fixtures',
)
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'django_taggsonomy',
)
SECRET_KEY = 'not very secret at all, actually'
