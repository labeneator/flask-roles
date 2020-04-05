# -*- coding: utf-8 -*-
from example.extensions import roles, db, principal, login_manager
from example import models
import werkzeug
from flask import Flask, Response, current_app, request
from flask_login import current_user, login_required, login_user
from flask_principal import (
    Identity,
    Permission,
    RoleNeed,
    identity_changed,
    identity_loaded,
)


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add any roles for the user
    for role_name in current_user.get_role_names():
        identity.provides.add(RoleNeed(role_name))

    # Add any roles for the user via group member_ship
    for group in current_user.groups:
        for role_name in group.get_role_names():
            identity.provides.add(RoleNeed(role_name))


@login_manager.unauthorized_handler
def unauthorized():
    return (
        Response("Bad User. Go away"),
        401,
    )


@login_manager.user_loader
def load_user(id):
    user = db.session.query(models.User).get(int(id))
    return user


def init_extensions(app):
    principal.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    roles.init_app(app)


def init_resources(app):
    @app.route("/login", methods=["post"])
    def login():
        user = (
            db.session.query(models.User)
            .filter_by(username=request.form.get("username"))
            .one()
        )
        login_user(user)
        # Tell Flask-Principal the identity changed
        identity_changed.send(
            current_app._get_current_object(), identity=Identity(user.id),
        )
        return Response("Yay!")

    # Public resource
    @app.route("/index")
    def index():
        return Response("index")

    # Private resource
    @app.route("/profile")
    @login_required
    def profile():
        return Response("profile")

    view_permission = Permission(RoleNeed("protected.view"))

    @app.route("/protected/view")
    @login_required
    @view_permission.require(403)
    def protected_view():
        return Response("view protected")


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "deterministic"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    @app.errorhandler(werkzeug.exceptions.Forbidden)
    def handle_bad_request(e):
        return (
            Response("Forbidden. Go away"),
            403,
        )

    return app


def init_users(app):
    with app.app_context():
        db.session.add(models.User(username="anon_user"))
        db.session.add(models.User(username="logged_in_user"))
        db.session.add(models.User(username="admin_via_role_user"))
        db.session.add(models.User(username="admin_via_group_user"))
        db.session.commit()


def init_group(app):
    with app.app_context():
        db.session.add(models.Group(name="admin"))
        db.session.commit()


def init_roles(app):
    with app.app_context():
        protected_view_role = models.Role(name="protected.view")
        db.session.add(protected_view_role)
        db.session.commit()

        # Add role to admin_via_role_user
        admin_user = (
            db.session.query(models.User)
            .filter_by(username="admin_via_role_user")
            .one()
        )
        admin_user.add_role(protected_view_role)

        # Add role to group admin_via_group
        admin_group = db.session.query(models.Group).one()
        admin_group.add_role(protected_view_role)

        # add admin_via_group_user to group
        admin_user = (
            db.session.query(models.User)
            .filter_by(username="admin_via_group_user")
            .one()
        )
        admin_user.groups.append(admin_group)


def main():
    app = create_app()
    init_extensions(app)
    with app.app_context():
        db.create_all()

    init_resources(app)
    init_users(app)
    init_group(app)
    init_roles(app)
    app.run(port=12345)


if __name__ == "__main__":
    main()
