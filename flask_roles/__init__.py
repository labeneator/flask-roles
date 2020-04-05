# -*-coding: utf-8
"""
    flask_roles
    ~~~~~~~~~~~~~

    Adds Roles support to a flask project
"""


from .model import GroupMixin, RoleMixin, UserMixin

__all__ = ["Roles", "RoleMixin", "UserMixin", "GroupMixin"]


class Roles(object):
    """This class implements role-based access control module in Flask. There
    are two way to initialize Flask-Roles::

        app = Flask(__name__)
        roles = Roles(app)

    or::

        roles = Roles
        def create_app():
            app = Flask(__name__)
            roles.init_app(app)
            return app

    :param app: the Flask object
    """

    def __init__(self, app=None):
        """Initialize with app."""
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        """Initialize application in Flask-Roles. Adds (Role, app) to flask
        extensions.

        :param app: Flask object
        """
