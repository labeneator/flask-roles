Usage
===============
The following section documents the typical use of this library



Define models to store your roles.

.. code-block:: python

  import flask_login
  import flask_roles

  from example.extensions import db


  class Role(db.Model, flask_roles.RoleMixin):
      """
      Role class. A role has the following properties
       - name: A textual representation e.g. accounts.send_money
       - parent: Optional reference to a parent role that owns this role.
      """
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
      """
      User class. Your Typical user class.
      You will need to add UserMixin from flask_login and flask_roles
      You may add helper properties roles and groups for your use cases:
       - roles: User has role assigned directly (user_role table stores the relationship)
       - groups: User is assigned to groups which have assigned roles.
      """
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
      """Stores user assigned roles"""
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
      """Stores group assigned roles"""
      group_id = db.Column(
          db.Integer, db.ForeignKey("group.id"), primary_key=True,
      )
      role_id = db.Column(
          db.Integer, db.ForeignKey("role.id"), primary_key=True,
      )


  class UserGroup(db.Model):
      """Stores assignments of users to groups"""
      group_id = db.Column(
          db.Integer, db.ForeignKey("group.id"), primary_key=True,
      )
      user_id = db.Column(
          db.Integer, db.ForeignKey("user.id"), primary_key=True,
      )


Import the library and decide on the initialisation method

.. code-block:: python

  from flask_roles import Roles
  roles = Roles()


Configure flask-Principal. We use RoleNeed and Permissions to enforce access

.. code-block:: python

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

      # Add any roles assigned to the user directly
      for role_name in current_user.get_role_names():
          identity.provides.add(RoleNeed(role_name))

      # Add any roles for the user via group member_ship
      for group in current_user.groups:
          for role_name in group.get_role_names():
              identity.provides.add(RoleNeed(role_name))



Configure flask-Login.

.. code-block:: python

  from flask_login import current_user, login_required, login_user

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


Configure flask and add your views and configure the view Permission

.. code-block:: python

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

    # .......
    # .......

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


    view_permission = Permission(RoleNeed("protected.view"))

    @app.route("/protected/view")
    @login_required
    @view_permission.require(403)
    def protected_view():
        return Response("view protected")


Protected view should be stored as a role in your datastore. Once a user logs in, flask principal laods the assigned role to current_user and verifies per role access on any view decorated with an instance of Permission(RoleNeed('myrole'))

You can nest roles into a tree like structure using the parent field.

For example

 - Superdmin is parent to accounts, shipping, admin roles
 - accounts is parent to accounts.create, accounts.expense roles
 - shipping is parent to shipping.dispatch, shipping.create ....
 
If you assign a user the role superadmin, the user will have full access to all aspects of your app. A user assigned
the role accounts will only have access to views assigned to accounts and its descedants.

The set of roles applied to the user is a union of roles assigned directly and roles assigned to groups the user belongs to.



