# -*- coding: utf-8 -*-
import flask_login
import flask_roles

from example.extensions import db


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
