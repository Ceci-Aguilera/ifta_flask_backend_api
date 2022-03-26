from datetime import date, timedelta
import decimal
from http import HTTPStatus
from http.client import HTTPResponse
from operator import and_
import os
from threading import Thread
from time import sleep

from flask_admin.contrib.sqla import ModelView, fields
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.actions import action
from flask_admin.form import Select2Widget
from flask import render_template, flash, Markup, Blueprint, send_from_directory, request, current_app
from wtforms.fields import PasswordField, BooleanField

# import flask_mail


from api.user_account.models import User, Driver, Truck
from api.quarter_entries.models import NewEntry, Quarter, StateTax, StateQuarterReport
from .models import UserAdmin


from flask_security import current_user, login_required, RoleMixin, Security, SQLAlchemyUserDatastore, UserMixin



class UserView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')

    column_exclude_list = ['password_hash',]

    form_excluded_columns = ['password_hash',]



class DriverView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')

    column_exclude_list = ['password_hash',]

    form_excluded_columns = ['password_hash',]


class TruckView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')


class NewEntryView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')


class QuarterView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')


class StateTaxView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')


class StateQuarterReportView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')


class UserAdminView(ModelView):

    column_exclude_list = ('password', 'confirmed_at',)
    form_excluded_columns = ('password', 'confirmed_at',)
    column_auto_select_related = True

    def is_accessible(self):
        return current_user.has_role('admin')

    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):

        if len(model.password2):
            model.password = utils.encrypt_password(model.password2)


class RoleAdminView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')

    def __hash__(self):
        return hash(self.name)