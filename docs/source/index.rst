=============
Pyramid Royal
=============

.. image:: https://travis-ci.org/hadrien/pyramid_royal.png?branch=master
   :target: https://travis-ci.org/hadrien/pyramid_royal

.. image:: https://coveralls.io/repos/hadrien/pyramid_royal/badge.png
   :target: https://coveralls.io/r/hadrien/pyramid_royal

.. image:: https://pypip.in/d/pyramid_royal/badge.png
   :target: https://crate.io/packages/pyramid_royal/


Royal is a pyramid extension which eases writing RESTful web applications.

It uses pyramid traversal algorithm rather than URL Dispatch as it offers a
neat pattern to represent REST resources.


Traversal quick overview
========================

.. Note::

   Refer to :ref:`request processing<pyramid:router_chapter>` and
   :ref:`traversal <pyramid:traversal_chapter>` chapters in pyramid
   documentation for details.

Using traversal, requesting ``/users/hadrien/photos/`` is treated as dict
accesses::

   RootFactory(request)['users']['hadrien']['photos']

A root factory object configured using
:meth:`pyramid.config.Configurator.set_root_factory` is instantiated for each
request.

A traverser function locates the context by traversing resources tree using any
existing ``__getitem__`` on the root object and subobjects.

When any of the ``__getitem__`` call raises a ``KeyError`` exception or
traverser reach the end of request's ``PATH_INFO``, context is found.

Then pyramid's router looks up a view callable using the context.


Collections and Items
=====================

.. Note::
   Refer to :ref:`Creating a Pyramid Project<pyramid:project_narr>` for details
   on pyramid configuration.

A REST API is a tree of resources accessible via HTTP methods. Here is an example with 3 resources, `user`, `photo` and `user photo`::

   root
   ├── photos             Collection of photos           /photos
   │   └── {photo_id}     Photo item                     /photos/123/
   └── users              Collection of users            /users/
       └── {user_id}      User item                      /users/hadrien/
           └── photos     Collection of user's photos    /users/hadrien/photos


2 ways to configure this tree of resources with royal:

   #. **Imperative** using ``config.add_resource``. By convention, directive will
      look for classes named ``Collection`` and/or ``Item`` in sub modules.

      * ``example/resource/__init__.py``::

         def includeme(config):
            config.add_resource('users')
            config.add_resource('users.photos')
            config.add_resource('photos')

      * ``example/resource/users.py``, ``example/resource/users_photos.py`` and
        ``example/resource/photos.py``::

         import royal

         class Collection(royal.Collection):
            pass

         class Item(royal.Item):
            pass

   #. **Declarative** using ``collection_config`` and ``item_config``
      decorator::

         import royal

         def incudeme(config):
            config.scan()

         @royal.collection_config('users')
         class Users(royal.Collection):

            def index(self, params):
               pass

         @royal.item_config('users')
         class User(royal.Item):

            def show(self, params):
               pass

TBD...

Changes
=======

.. include:: ../../CHANGES.rst
