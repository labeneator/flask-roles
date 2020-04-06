Flask-Roles
=======================================

Flask-Roles is a flask extensions that adds role access control support.



Installation
===============
Installing the client is simple with pip:

.. code-block:: sh

    pip install flask-roles


Running Tests
===============

.. code-block:: sh

    # tox -e check
    # tox



Docs
===============

You may access the `docs`_ 

.. _docs: https://flask-roles.readthedocs.io/en/latest/

Or build them locally

.. code-block:: sh

    # tox -e docs



Proof of Concept
==================

After installing the client, Use the mixins to enrich your sqlalchemy classes, initialise flask-login and flask-principal. 
For each resource that needs role protection, define a roleneed and decorate the resource.

Start the example:

.. code-block:: sh

  # export PYTHONPATH=$(pwd)
  # cd example
  # ../.tox/py37/bin/python app.py  ## assumes you have run tox before
 

An anonymouse user has no access to pages which require login or have a role protection

.. code-block:: text

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


A logged in user with no roles has no access to pages which have a role protection

.. code-block:: text


	# Log in the user

	 ❯ http --form --session=logged_in_user POST http://127.0.0.1:12345/login username=logged_in_user
	HTTP/1.0 200 OK
	Content-Length: 4
	Content-Type: text/html; charset=utf-8
	Date: Sun, 05 Apr 2020 14:02:43 GMT
	Server: Werkzeug/1.0.1 Python/3.7.7
	Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey29FOYyzPB4LzO3Q8_FTP249GbmVcxkQCFqrq7EojblnAgaMiWL4KTWrB7USWBxydkEJTMzgU2VI5UIJKEWF6CG6KWqIIZWGxH7DAjRc0aPQAPYBJRLG3AUj1gkuzJihsh16vGz8aOuontf-_NOV1_m_nyomfZr2_6W79e_P-2mPsI.XonlAw.Lh27l4yyfujMboQyNee_Ir5NITo; HttpOnly; Path=/
	Vary: Cookie

	Yay!


	 ❯ http  --session=logged_in_user  http://127.0.0.1:12345/index
	HTTP/1.0 200 OK
	Content-Length: 5
	Content-Type: text/html; charset=utf-8
	Date: Sun, 05 Apr 2020 14:03:16 GMT
	Server: Werkzeug/1.0.1 Python/3.7.7
	Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey29FOYyzPB4LzO3Q8_FTP249GbmVcxkQCFqrq7EojblnAgaMiWL4KTWrB7USWBxydkEJTMzgU2VI5UIJKEWF6CG6KWqIIZWGxH7DAjRc0aPQAPYBJRLG3AUj1gkuzJihsh16vGz8aOuontf-_NOV1_m_nyomfZr2_6W79e_P-2mPsI.XonlJA.7Uapa_a1fE9zhwLIkI2F81kjFY0; HttpOnly; Path=/
	Vary: Cookie

	index


	 ❯ http  --session=logged_in_user  http://127.0.0.1:12345/profile  
	HTTP/1.0 200 OK
	Content-Length: 7
	Content-Type: text/html; charset=utf-8
	Date: Sun, 05 Apr 2020 14:03:24 GMT
	Server: Werkzeug/1.0.1 Python/3.7.7
	Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey29FOYyzPB4LzO3Q8_FTP249GbmVcxkQCFqrq7EojblnAgaMiWL4KTWrB7USWBxydkEJTMzgU2VI5UIJKEWF6CG6KWqIIZWGxH7DAjRc0aPQAPYBJRLG3AUj1gkuzJihsh16vGz8aOuontf-_NOV1_m_nyomfZr2_6W79e_P-2mPsI.XonlLA.D4x6uJeVXmlK_LqMxv_qaR812cM; HttpOnly; Path=/
	Vary: Cookie

	profile


	 ❯ http  --session=logged_in_user  http://127.0.0.1:12345/protected/view 
	HTTP/1.0 403 FORBIDDEN
	Content-Length: 18
	Content-Type: text/html; charset=utf-8
	Date: Sun, 05 Apr 2020 14:03:40 GMT
	Server: Werkzeug/1.0.1 Python/3.7.7
	Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey29FOYyzPB4LzO3Q8_FTP249GbmVcxkQCFqrq7EojblnAgaMiWL4KTWrB7USWBxydkEJTMzgU2VI5UIJKEWF6CG6KWqIIZWGxH7DAjRc0aPQAPYBJRLG3AUj1gkuzJihsh16vGz8aOuontf-_NOV1_m_nyomfZr2_6W79e_P-2mPsI.XonlPA.0KQs2WnXJFB_JJr6iedA_sT7a3M; HttpOnly; Path=/
	Vary: Cookie

	Forbidden. Go away


A logged in user with a role directly assigned can access a protected resource

.. code-block:: text

  ❯ http --form --session=admin_via_role POST http://127.0.0.1:12345/login username=admin_via_role_user 
  HTTP/1.0 200 OK
  Content-Length: 4
  Content-Type: text/html; charset=utf-8
  Date: Sun, 05 Apr 2020 14:09:43 GMT
  Server: Werkzeug/1.0.1 Python/3.7.7
  Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey30UJjLMMPjvczcDj0XM_Xj0puZVzGTAYWouboSi9qUcyJoyJQsgpNas3pQJ4HFJWcTlMzMBDZVjlQikIRaXIAaopeqghhabUTsMyBEzxk9Ag1gE1AubcBRPGKR7MqIGSLXqcfPZtRVdO9rf97p6svcnw81035t29_y_cL7A-3VPsQ.Xonmpw.O8o2nJaFyqoZGiCVjavak7pjzDs; HttpOnly; Path=/
  Vary: Cookie

  Yay!


   ❯ http  --session=admin_via_role  http://127.0.0.1:12345/index 
  HTTP/1.0 200 OK
  Content-Length: 5
  Content-Type: text/html; charset=utf-8
  Date: Sun, 05 Apr 2020 14:09:48 GMT
  Server: Werkzeug/1.0.1 Python/3.7.7
  Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey30UJjLMMPjvczcDj0XM_Xj0puZVzGTAYWouboSi9qUcyJoyJQsgpNas3pQJ4HFJWcTlMzMBDZVjlQikIRaXIAaopeqghhabUTsMyBEzxk9Ag1gE1AubcBRPGKR7MqIGSLXqcfPZtRVdO9rf97p6svcnw81035t29_y_cL7A-3VPsQ.XonmrA.47Px1lEdKHRGQitDOWmN-78B7jA; HttpOnly; Path=/
  Vary: Cookie

  index


   ❯ http  --session=admin_via_role  http://127.0.0.1:12345/profile 
  HTTP/1.0 200 OK
  Content-Length: 7
  Content-Type: text/html; charset=utf-8
  Date: Sun, 05 Apr 2020 14:09:51 GMT
  Server: Werkzeug/1.0.1 Python/3.7.7
  Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey30UJjLMMPjvczcDj0XM_Xj0puZVzGTAYWouboSi9qUcyJoyJQsgpNas3pQJ4HFJWcTlMzMBDZVjlQikIRaXIAaopeqghhabUTsMyBEzxk9Ag1gE1AubcBRPGKR7MqIGSLXqcfPZtRVdO9rf97p6svcnw81035t29_y_cL7A-3VPsQ.Xonmrw.EzqUDUEP0mp4wrj3tEX5fUmaIjA; HttpOnly; Path=/
  Vary: Cookie

  profile


   ❯ http  --session=admin_via_role  http://127.0.0.1:12345/protected/view 
  HTTP/1.0 200 OK
  Content-Length: 14
  Content-Type: text/html; charset=utf-8
  Date: Sun, 05 Apr 2020 14:09:53 GMT
  Server: Werkzeug/1.0.1 Python/3.7.7
  Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey30UJjLMMPjvczcDj0XM_Xj0puZVzGTAYWouboSi9qUcyJoyJQsgpNas3pQJ4HFJWcTlMzMBDZVjlQikIRaXIAaopeqghhabUTsMyBEzxk9Ag1gE1AubcBRPGKR7MqIGSLXqcfPZtRVdO9rf97p6svcnw81035t29_y_cL7A-3VPsQ.XonmsQ.khbch6e1tJwDWrWNpFJiBzxbq7Q; HttpOnly; Path=/
  Vary: Cookie

  view protected


A logged in user in a group that has an assigned role can access a protected resource

.. code-block:: text

  ❯ http --form --session=admin_via_group POST http://127.0.0.1:12345/login username=admin_via_group_user 
  HTTP/1.0 200 OK
  Content-Length: 4
  Content-Type: text/html; charset=utf-8
  Date: Sun, 05 Apr 2020 14:11:59 GMT
  Server: Werkzeug/1.0.1 Python/3.7.7
  Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey29FOYyzPB4LzO3Q8_FTP249GbmVcxkQCFqrq7EojblnAgaMiWL4KTWrB7USWBxydkEJTMzgU2VI5UIJKEWF6CG6KWqIIZWGxH7DAjRc0aPQAPYBJRLG3AUj1gkuzJihsh16vGzCaOuontf-_NOV1_m_nyomfZr2_6W7ze8P-4EPsY.XonnLw.gcxu0FnLw3SW2nt9v300OkOj9eQ; HttpOnly; Path=/
  Vary: Cookie

  Yay!


   ❯ http  --session=admin_via_group  http://127.0.0.1:12345/index  
  HTTP/1.0 200 OK
  Content-Length: 5
  Content-Type: text/html; charset=utf-8
  Date: Sun, 05 Apr 2020 14:12:08 GMT
  Server: Werkzeug/1.0.1 Python/3.7.7
  Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey29FOYyzPB4LzO3Q8_FTP249GbmVcxkQCFqrq7EojblnAgaMiWL4KTWrB7USWBxydkEJTMzgU2VI5UIJKEWF6CG6KWqIIZWGxH7DAjRc0aPQAPYBJRLG3AUj1gkuzJihsh16vGzCaOuontf-_NOV1_m_nyomfZr2_6W7ze8P-4EPsY.XonnOA.Po7p1SX1uxwFIkp4xryoLUIifAE; HttpOnly; Path=/
  Vary: Cookie

  index


   ❯ http  --session=admin_via_group  http://127.0.0.1:12345/profile  
  HTTP/1.0 200 OK
  Content-Length: 7
  Content-Type: text/html; charset=utf-8
  Date: Sun, 05 Apr 2020 14:12:12 GMT
  Server: Werkzeug/1.0.1 Python/3.7.7
  Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey29FOYyzPB4LzO3Q8_FTP249GbmVcxkQCFqrq7EojblnAgaMiWL4KTWrB7USWBxydkEJTMzgU2VI5UIJKEWF6CG6KWqIIZWGxH7DAjRc0aPQAPYBJRLG3AUj1gkuzJihsh16vGzCaOuontf-_NOV1_m_nyomfZr2_6W7ze8P-4EPsY.XonnPA.67de6ypYuBrVfOCHPx9QeF0WpoU; HttpOnly; Path=/
  Vary: Cookie

  profile


   ❯ http  --session=admin_via_group  http://127.0.0.1:12345/protected/view
  HTTP/1.0 200 OK
  Content-Length: 14
  Content-Type: text/html; charset=utf-8
  Date: Sun, 05 Apr 2020 14:12:18 GMT
  Server: Werkzeug/1.0.1 Python/3.7.7
  Set-Cookie: session=.eJxNjsEKwyAQRP_Fcynqqqv5mbDrriQQQknMoZT-ey29FOYyzPB4LzO3Q8_FTP249GbmVcxkQCFqrq7EojblnAgaMiWL4KTWrB7USWBxydkEJTMzgU2VI5UIJKEWF6CG6KWqIIZWGxH7DAjRc0aPQAPYBJRLG3AUj1gkuzJihsh16vGzCaOuontf-_NOV1_m_nyomfZr2_6W7ze8P-4EPsY.XonnQg.-Kd16RdiOItgCRg69jqYXE35ck8; HttpOnly; Path=/
  Vary: Cookie

  view protected
