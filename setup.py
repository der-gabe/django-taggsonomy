import setuptools

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-taggsonomy',
    version='0.0.1',
    author='Gabriel Niebler',
    author_email='gabriel.niebler@gmail.com',
    description='Advanced tagging engine for Django',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/der-gabe/django-taggsonomy',
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'django_taggsonomy': [
            'src/taggsonomy/static',
            'src/taggsonomy/templates',
        ]
    },
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'django_colorinput',
    ],
    python_requires='>=3.6',
)
