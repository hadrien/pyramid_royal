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

TBD
