# -*- coding: utf-8 -*-
from unittest import TestCase

import flask_login
import flask_roles
import werkzeug
from flask import Flask, Response, current_app, request
from flask_login import LoginManager, current_user, login_required, login_user
from flask_principal import (
    Identity,
    Permission,
    Principal,
    RoleNeed,
    identity_changed,
    identity_loaded,
)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
principal = Principal()


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


class Role(db.Model, flask_roles.RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    children = db.relationship(
        "Role",
        lazy="joined",
        join_depth=2,
        order_by=id,
        backref=db.backref("parent", remote_side=[id]),
    )

    def __repr__(self):
        return "<Role %r>" % self.name


class User(db.Model, flask_login.UserMixin, flask_roles.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    active = db.Column(db.Boolean, default=True)
    roles = db.relationship(
        "Role",
        secondary="user_role",
        backref=db.backref("roles", lazy="dynamic"),
    )
    groups = db.relationship(
        "Group", secondary="user_group", backref=db.backref("users"),
    )

    def __repr__(self):
        return "<User %r>" % self.username


class UserRole(db.Model):
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True,
    )
    role_id = db.Column(
        db.Integer, db.ForeignKey("role.id"), primary_key=True,
    )


class Group(db.Model, flask_roles.GroupMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    roles = db.relationship(
        "Role",
        secondary="group_role",
        backref=db.backref("groups", lazy="dynamic"),
    )

    def __repr__(self):
        return "<Group %r>" % self.name


class GroupRole(db.Model):
    group_id = db.Column(
        db.Integer, db.ForeignKey("group.id"), primary_key=True,
    )
    role_id = db.Column(
        db.Integer, db.ForeignKey("role.id"), primary_key=True,
    )


class UserGroup(db.Model):
    group_id = db.Column(
        db.Integer, db.ForeignKey("group.id"), primary_key=True,
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True,
    )


class RolesTest(TestCase):
    TESTING = True

    def setUp(self):
        self.create_app()
        self.login_manager = LoginManager()
        self.init_db()
        with self.app.test_request_context():
            db.create_all()
        self.init_login_manager()
        principal.init_app(self.app)

    def tearDown(self):
        db.session.remove()
        with self.app.test_request_context():
            db.drop_all()

        del self.client
        del self.app

    def create_app(self):
        self.app = Flask(__name__)

        self.app.config["SECRET_KEY"] = "deterministic"
        self.app.config["SESSION_PROTECTION"] = None
        self.remember_cookie_name = "remember"
        self.app.config["REMEMBER_COOKIE_NAME"] = self.remember_cookie_name
        # self.login_manager = LoginManager()
        # self.login_manager.init_app(self.app)
        self.app.config["LOGIN_DISABLED"] = False

        # self.app.config["TESTING"] = False
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        self.client = self.app.test_client()

        @self.app.errorhandler(werkzeug.exceptions.Forbidden)
        def handle_bad_request(e):
            return (
                Response("Forbidden. Go away"),
                403,
            )

        return self.app

    def init_principal(self):
        principal.init_app(self.app)

    def init_login_manager(self):
        self.login_manager.init_app(self.app)

        @self.login_manager.unauthorized_handler
        def unauthorized():
            return (
                Response("Bad User. Go away"),
                401,
            )

        @self.login_manager.user_loader
        def load_user(id):
            user = db.session.query(User).get(int(id))
            return user

    def init_roles(self, via_factory=True):
        if via_factory:
            self.roles = flask_roles.Roles()
            self.roles.init_app(self.app)
        else:
            self.roles = flask_roles.Roles(self.app)

    def init_db(self):
        db.init_app(self.app)

    def init_app_routes(self, via_factory=True):
        self.init_roles(via_factory)
        # Public resource
        @self.app.route("/login", methods=["post"])
        def login():
            user = (
                db.session.query(User)
                .filter_by(username=request.form.get("username"))
                .one()
            )
            login_user(user, remember=True)
            # Tell Flask-Principal the identity changed
            identity_changed.send(
                current_app._get_current_object(), identity=Identity(user.id),
            )
            return Response("Yay!")

        # Public resource
        @self.app.route("/index")
        def index():
            return Response("index")

        # Private resource
        @self.app.route("/profile")
        @login_required
        def profile():
            return Response("profile")

        view_permission = Permission(RoleNeed("protected.view"))

        @self.app.route("/protected/view")
        @login_required
        @view_permission.require(403)
        def protected_view():
            return Response("view protected")

        create_permission = Permission(RoleNeed("protected.create"))

        @self.app.route("/protected/create")
        @login_required
        @create_permission.require(403)
        def protected_create():
            return Response("create protected")

    def mk_user(self, username="test_user"):
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        return user

    def mk_role(self, name, parent=None):
        role = Role(name=name, parent=parent)
        db.session.add(role)
        db.session.commit()
        return role

    def mk_group(self, name):
        group = Group(name=name)
        db.session.add(group)
        db.session.commit()
        return group

    def test_no_logged_in_user_test_case(self):
        self.init_app_routes()
        with self.app.test_request_context():
            self.assertTrue(current_user.is_anonymous)

        with self.client:
            self.assertEqual(self.client.open("/index").data, b"index")
            self.assertEqual(
                self.client.open("/profile").data, b"Bad User. Go away"
            )

            self.assertEqual(
                self.client.open("/protected/view").data, b"Bad User. Go away"
            )
            self.assertEqual(
                self.client.open("/protected/create").data,
                b"Bad User. Go away",
            )

    def test_logged_in_user_no_role_test_case(self):
        self.init_app_routes()
        with self.app.test_request_context():
            self.mk_user()
        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")

            # we have no access to protected view due to missing roles
            self.assertEqual(
                self.client.open("/protected/view").data, b"Forbidden. Go away"
            )
            self.assertEqual(
                self.client.open("/protected/create").data,
                b"Forbidden. Go away",
            )

    def test_logged_in_user_with_a_role_test_case(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            protected_view_role = self.mk_role("protected.view")
            user.add_role(protected_view_role)
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"view protected"
            )
            self.assertEqual(
                self.client.open("/protected/create").data,
                b"Forbidden. Go away",
            )

    def test_logged_in_with_a_different_role_test_case(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            protected_create_role = self.mk_role("protected.create")
            user.add_role(protected_create_role)
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data,
                b"Forbidden. Go away",
            )
            self.assertEqual(
                self.client.open("/protected/create").data, b"create protected"
            )

    def test_logged_in_with_multiple_roles_test_case(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            protected_view_role = self.mk_role("protected.view")
            user.add_role(protected_view_role)
            protected_create_role = self.mk_role("protected.create")
            user.add_role(protected_create_role)
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"view protected"
            )
            self.assertEqual(
                self.client.open("/protected/create").data, b"create protected"
            )

    def test_logged_in_user_with_ancestor_role_case(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            # Parent role
            protected_role = self.mk_role("protected")
            # Make these roles childrent of protected_role
            self.mk_role("protected.view", parent=protected_role)
            self.mk_role("protected.create", parent=protected_role)
            # Grant user access to protected role and consequently,
            # any children role
            user.add_role(protected_role)
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"view protected"
            )
            self.assertEqual(
                self.client.open("/protected/create").data, b"create protected"
            )

    def test_logged_in_user_with_grand_children_role_case(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            # Parent role
            admin_role = self.mk_role("admin")
            # Child role
            protected_role = self.mk_role("protected", parent=admin_role)
            # Make grandchildren of admin_role
            self.mk_role("protected.view", parent=protected_role)
            self.mk_role("protected.create", parent=protected_role)
            # Grant user access to admin role and consequently,
            # any children role
            user.add_role(admin_role)
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"view protected"
            )
            self.assertEqual(
                self.client.open("/protected/create").data, b"create protected"
            )

    def test_logged_in_user_in_a_group_with_no_role(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            group = self.mk_group("viewers")
            user.groups.append(group)
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"Forbidden. Go away"
            )
            self.assertEqual(
                self.client.open("/protected/create").data,
                b"Forbidden. Go away",
            )

    def test_logged_in_user_in_a_group_with_a_role(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            group = self.mk_group("creators")
            user.groups.append(group)

            protected_create_role = self.mk_role("protected.create")
            group.add_role(protected_create_role)
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"Forbidden. Go away"
            )
            self.assertEqual(
                self.client.open("/protected/create").data, b"create protected"
            )

    def test_logged_in_user_in_a_group_with_roles(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            group = self.mk_group("protectors")
            user.groups.append(group)

            group.add_role(self.mk_role("protected.create"))
            group.add_role(self.mk_role("protected.view"))
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"view protected"
            )
            self.assertEqual(
                self.client.open("/protected/create").data, b"create protected"
            )

    def test_logged_in_user_in_a_group_with_roles_added_via_add_roles(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            group = self.mk_group("protectors")
            user.groups.append(group)

            group.add_roles(
                [
                    self.mk_role("protected.create"),
                    self.mk_role("protected.view"),
                ]
            )
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"view protected"
            )
            self.assertEqual(
                self.client.open("/protected/create").data, b"create protected"
            )

    def test_logged_in_user_in_a_group_with_ancestry_roles(self):
        self.init_app_routes()
        with self.app.test_request_context():
            user = self.mk_user()
            group = self.mk_group("admins")
            user.groups.append(group)

            # Parent role
            admin_role = self.mk_role("admin")
            # Child role
            protected_role = self.mk_role("protected", parent=admin_role)
            # Make grandchildren of admin_role
            self.mk_role("protected.view", parent=protected_role)
            self.mk_role("protected.create", parent=protected_role)
            # Grant user access to admin role and consequently,
            # any children role

            group.add_role(admin_role)
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"view protected"
            )
            self.assertEqual(
                self.client.open("/protected/create").data, b"create protected"
            )

    def test_roles_init_with_via_factory_false(self):
        self.init_app_routes(via_factory=False)
        with self.app.test_request_context():
            user = self.mk_user()
            group = self.mk_group("creators")
            user.groups.append(group)

            protected_create_role = self.mk_role("protected.create")
            group.add_role(protected_create_role)
            db.session.commit()

        with self.client:
            self.client.post("/login", data=dict(username="test_user"))
            self.assertEqual(current_user.username, "test_user")
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(self.client.get("/profile").data, b"profile")
            self.assertEqual(
                self.client.open("/protected/view").data, b"Forbidden. Go away"
            )
            self.assertEqual(
                self.client.open("/protected/create").data, b"create protected"
            )
