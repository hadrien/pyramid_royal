----------------------
Code for the impatient
----------------------

The example is available `on the code repository
<http://github.com/hadrien/pyramid_royal>`_

Code
----


:file:`example/resources/__init__.py`

.. literalinclude:: ../../example/resources/__init__.py

:file:`example/resources/users.py`

.. literalinclude:: ../../example/resources/users.py

:file:`example/resources/users_photos.py`

.. literalinclude:: ../../example/resources/users_photos.py


Result
------

.. http:get:: /users?offset=20&limit=20

   .. sourcecode:: http

      Response: 200 OK
      Content-Type: application/json; charset=UTF-8

      {
         "first": "http://localhost/users/?limit=20&offset=0",
         "previous": "http://localhost/users/?limit=20&offset=0",
         "next": "http://localhost/users/?limit=20&offset=40",
         "href": "http://localhost/users/?limit=20&offset=20",
         "users": [
             {
                 "username": "user29",
                 "photos": {
                     "href": "http://localhost/users/user29/photos/"
                 },
                 "_id": "52f956a50c72dceb3f143584",
                 "email": "user29@email.com",
                 "href": "http://localhost/users/user29/"
             },
             {
                 "username": "user28",
                 "photos": {
                     "href": "http://localhost/users/user28/photos/"
                 },
                 "_id": "52f956a50c72dceb3f143583",
                 "email": "user28@email.com",
                 "href": "http://localhost/users/user28/"
             },

             ...

             {
                 "username": "user10",
                 "photos": {
                     "href": "http://localhost/users/user10/photos/"
                 },
                 "_id": "52f956a50c72dceb3f143571",
                 "email": "user10@email.com",
                 "href": "http://localhost/users/user10/"
             }
         ]
      }


.. http:post:: /users/hadrien/photos

   .. sourcecode:: http

      Response: 201 Created
      Content-Type: application/json; charset=UTF-8
      Location: http://localhost/photos/52f95bb10c72dcebeffef163/

   .. sourcecode:: javascript

      {
          "href": "http://localhost/photos/52f95bb10c72dcebeffef163/",
          "_id": "52f95bb10c72dcebeffef163",
          "author": {
              "href": "http://localhost/users/hadrien/"
          }
      }
