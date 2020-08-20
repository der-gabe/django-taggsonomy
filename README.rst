=================
django-taggsonomy
=================

Advanced tagging engine for Django.

This project is mainly an exploration of some ideas about "advanced" features
that a tagging system could (and maybe should) have, to make it (even) more
useful to its users.

Quickstart
##########

Install ``django-taggsonomy`` and its dependency ``django-colorinput`` and add
them both to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        …
        'colorinput.apps.ColorInputConfig',
        'django_taggsonomy.apps.TaggsonomyConfig',
        …
    )

Also add ``django-taggsonomy``\'s URLS to your project's URLconf (``urls.py``),
like so:

.. code-block:: python

    urlpatterns = [
        …
        path('tags/', include('django_taggsonomy.urls')),
        …
    ]

That's it! Thanks to the magic of `Django's contenttypes framework
<https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/>`_ *all* your
models are now fully taggable. You now have the following ways to make use of
the tagging functionality:

Templatetags
============

``django-taggsonomy`` offers several templatetags that may be used directly in
templates using Django's templating engine to make objects taggable. To make use
of these templatetags, simply include

.. code-block::

    {% load taggsonomy %}

near the top of your template. Then you can add

.. code-block::

   {% tags object %}

anywhere in your template, to render a ``div`` container displaying the tags of
the ``object`` model instance (which must, of course, be defined in that
context).

There is also a ``tag_manager`` templatetag, which is used the same way, but
makes the tags removable (by clicking on a small 'x' on their right-hand side),
includes a form for adding new tags to the object and a link to some tag
management pages (templates for which are provided).

``TaggableMixin``
=================

While the above `Templatetags`_ make the inclusion of object tags in templates
trivial, and thus allow immediately working with tags via your application's
WebUI, they don't allow you to access and modify tags *in code*.

To this end, ``django-taggsonomy`` also provides a mixin called ``TaggableMixin``
in the module ``django_taggsonomy.mixins`` that taggable model's can inherit
from. All this does is that it adds an attribute named ``tags`` to each object,
which exposes the object's tag set (cf. `Tag sets`_).

While adding this mixin changes your model class's signature, it does not add,
remove or change a model field, so it doesn't necessitate a new migration.

A *decorator* for taggable models, which would leave the class signature alone,
is planned for the future.

Utility functions
=================

A few utility functions are provided in ``django_taggsonomy.mixins``:

1. ``get_tag_object`` to get a ``Tag`` object from its name or ID.
2. ``get_tagset_for_object`` to get the tag set for a given model instance,
   if it exists.
3. ``get_or_create_tagset_for_object`` to get the tag set for a given model
   instance, or create one if it doesn't exist.

Basic features
##############

Basic attributes
================

At the most basic level, a tag has a (unique) name and a colour.

Basic tag relations
===================

Exclusions
----------

A given tag may exclude (an)other tag(s), which means an object tagged with it
may not also be tagged with (one of) the excluded tag(s). Likewise, an object
tagged with (one of) the excluded tag(s) may not also be tagged with the tag in
question. Logically, exclusion is always bi-directional. Tags that exclude one
another are called "mutually exclusive".

Tagging an object with a new tag will remove any tags excluded by the one that's
added.

For instance, if there are two mutually exclusive tags named *TODO* and *DONE*,
then an object may only be tagged as **either** *TODO* **or** *DONE*, but **not
both** at the same time.
If an object has the *TODO* tag and gets tagged as *DONE*, the *TODO* tag is
automatically removed.

One could then add a third tag named *DOING* and have it exclude both *TODO* and
*DONE*. As a result, tagging a *TODO* item with *DOING* would remove the *TODO*
tag and tagging it as *DONE* later would then remove the *DOING* tag.

Inclusions (Subtags and Supertags)
----------------------------------

A given tag may have one or several so-called **supertags** so that tagging an
object with said tag will automatically also add those supertags (and *their*
supertags, all the way up).

The tag in question would be called a **subtag** of each of its supertags (which
may also have other subtags beside the given one) and they would be said to
**include** it.

For example, if there's a tag named *Django* and a tag named *Python*, then one
might wish for all objects tagged with *Django* to also be tagged with
*Python*.
This can be achieved by letting the *Python* tag **include** the *Django* tag
(i.e. the *Python* tag would be a **supertag** of the *Django* tag and the
*Django* tag would be a **subtag** of the *Python* tag).

The nomenclature here derives from set theory as, in the above example, the set
of objects tagged with *Python* would be a **super**\set of the set of objects
tagged with *Django* (and thus **include** it) and the latter set would be a
**sub**\set of the former.

Tag inclusions form a logical hierarchy of tags. (Where the hierarchy's
structure is not a tree, but a directed, acyclic graph.)

Concepts
########

Tag sets
========

At the programmatic heart of taggsonomy is the concept (and implementation) of
the so-called "tag set". As the name suggests, it does indeed behave like a
``set``, i.e. it implements all of the methods (regular or magic) one would
expect from a ``set`` (or at least it really should) including some additional
methods (and logic included in `set`-derived methods) to implement above
mentioned features (cf. `Basic tag relations`_).

Every taggable object has its own tag set, which may be reachable under the
``tags`` attribute.

Besides that, tags also have their dependent tag sets for exclusions, supertags
and subtags.
