class RoleMixin(object):
    def get_children(self):
        yield self
        for child in self.children:
            yield child
            for grandchild in child.get_children():
                yield grandchild


class UserMixin(object):
    def add_role(self, role):
        self.roles.append(role)

    def add_roles(self, roles):
        for role in roles:
            self.add_role(role)

    def get_roles(self):
        # Traverse any role which has this role
        # as an ancestor
        for role in self.roles:
            yield role
            for child_role in role.get_children():
                yield child_role

    def get_role_names(self):
        for role in self.get_roles():
            yield role.name


class GroupMixin(UserMixin):
    pass
