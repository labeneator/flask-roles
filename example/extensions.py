# -*- coding: utf-8 -*-
from flask_login import LoginManager
from flask_principal import Principal
from flask_roles import Roles
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
principal = Principal()
login_manager = LoginManager()
roles = Roles()
