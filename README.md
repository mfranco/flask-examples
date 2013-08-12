Flask User API
=================

A simple User RESTFUL API built using Flask Framework (http://flask.pocoo.org/) and Sqlalchemy
(http://www.sqlalchemy.org/)

Requirements
------------
Python 2.7.x


Installation
-------------

1. Create a virtual with:

        mkvirtualenv flaskapi
        workon flaskapi


2. Install requirements file:

        pip install -r requirements.txt


3. Run unit test suite:

        python manage.py test


4. Run app:

        python manage.py runserver


User API
----------

The main goal is desing and built a RestFull API that handles user registration and login for a new service 
(let's say a music service but could be anything). The API format will be JSON. The first thing that we must do
is define a root url: ::

    http://[hostname]/mymusic/api/v1.0/



See also
---------
[Flask Framework Website](http://flask.pocoo.org)

[Flask python3 support](http://flask.pocoo.org/docs/python3/)

[Sqlalchemy Website](http://www.sqlalchemy.org/)

[Designing a RESTful API with Python and Flask](http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask)

[Unit testing framework](http://docs.python.org/2/library/unittest.html)

[argparse — Parser for command-line options, arguments and sub-commands](http://docs.python.org/dev/library/argparse.html)

[Python @property versus getters and setters](http://stackoverflow.com/questions/6618002/python-property-versus-getters-and-setters)
