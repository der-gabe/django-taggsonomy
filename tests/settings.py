DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        }
}
FIXTURE_DIRS = (
    'fixtures',
)
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'taggsonomy',
)
SECRET_KEY = 'not very secret at all, actually'
