Flask-Roles
=======================================

Flask-Roles is a flask extensions that adds role access control support.



Installation
===============
Installing the client is simple with pip:

.. code-block:: sh

    pip install flask-roles


Quickstart
=============

After installing the client, Use the mixins to enrich your sqlalchemy classes, initialise flask-login and flask-principal. 
For each resource that needs role protection, define a roleneed and decorate the resource.

Start the example:

.. code-block:: sh
# export PYTHONPATH=$(pwd)
# cd example
# ../.tox/py37/bin/python app.py  ## assumes you have run tox before
 

An anonymouse user has no access to pages which require login or have a role protection

.. code-block:: sh

 ❯ http http://127.0.0.1:12345/index
HTTP/1.0 200 OK
Content-Length: 5
Content-Type: text/html; charset=utf-8
Date: Sun, 05 Apr 2020 13:46:09 GMT
Server: Werkzeug/1.0.1 Python/3.7.7

index


 ❯ http http://127.0.0.1:12345/profile 
HTTP/1.0 401 UNAUTHORIZED
Content-Length: 17
Content-Type: text/html; charset=utf-8
Date: Sun, 05 Apr 2020 13:46:18 GMT
Server: Werkzeug/1.0.1 Python/3.7.7

Bad User. Go away


 ❯ http http://127.0.0.1:12345/protected/view
HTTP/1.0 401 UNAUTHORIZED
Content-Length: 17
Content-Type: text/html; charset=utf-8
Date: Sun, 05 Apr 2020 13:46:33 GMT
Server: Werkzeug/1.0.1 Python/3.7.7

Bad User. Go away


