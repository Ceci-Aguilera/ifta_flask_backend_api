from config import db
from flask_security import current_user, login_required, RoleMixin, Security, SQLAlchemyUserDatastore, UserMixin

roles_users = db.Table('roles_useradmins',
        db.Column('useradmin_id', db.Integer(), db.ForeignKey('useradmin.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Role {self.id} - {self.name}>"

class UserAdmin(db.Model, UserMixin):
    __tablename__ = 'useradmin'
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('useradmins', lazy='dynamic'))
    amount_owned_to_admin = db.Column(db.Float(), default=0.0)

    def update(self):
        db.session.commit()

    def __str__(self):
        return str(self.id) + " - "+ str(self.email)

    def __repr__(self):
        if self.has_role('admin'):
            return f"<Admin {self.id} - {self.email}>"
        else:
            return f"<Staff {self.id} - {self.email}>"