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
        'taggsonomy': [
            'src/taggsonomy/templates/taggsonomy/active_tags.html',
            'src/taggsonomy/templates/taggsonomy/add_tags.html',
            'src/taggsonomy/templates/taggsonomy/tag.html',
            'src/taggsonomy/templates/taggsonomy/tag_confirm_delete.html',
            'src/taggsonomy/templates/taggsonomy/tag_create_form.html',
            'src/taggsonomy/templates/taggsonomy/tag_edit_form.html',
            'src/taggsonomy/templates/taggsonomy/tag_list.html',
            'src/taggsonomy/templates/taggsonomy/tag_manager.html',
            'src/taggsonomy/templates/taggsonomy/tags.html',
        ],
    },
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
