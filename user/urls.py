'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from .models import User, Team
import logging
import tornado
from tornado.options import options
from tornado.web import RequestHandler
import hashlib
from core.BaseHandler import BaseHandler 
from forms import Form, TextField
from core.database import db


class SigninForm(Form):
    email = TextField('email')
    password = TextField('password')

class LoginHandler(BaseHandler):
    _error_message = "email or password incorrect!"
    def get(self):
        self.render("login.html")

    def post(self):
        form = SigninForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            m = hashlib.md5()
            m.update(('%s%s%s'%(options.salt, 
                               form.email.data, 
                               form.password.data)).encode('utf-8'))
            password_md5 = m.hexdigest()
            print(password_md5)
            currentUser = User.query.filter_by(email=form.email.data, password=password_md5).first()
        if currentUser is None:
            self.render("login.html", form = form, errorMessage = self._error_message)
        else:
            self.set_secure_cookie("sid", self.session.sessionid)
            self.session["user"] = currentUser
            self.session["currentTeamId"] = 1
            self.redirect("/")

class SettingForm(Form):
    email = TextField('email')
    name = TextField('name')
    nickName = TextField('nickName')
    password = TextField('password')
    confirmPassword = TextField('confirmPassword')

class SettingHandler(BaseHandler):
    _error_message = 'password and confirm password not same'
    @tornado.web.authenticated
    def get(self):
        currentUser = self.current_user
        user = User.query.filter_by(id=currentUser.id).first()
        self.render("settings/user.html", currentUser= user)

    @tornado.web.authenticated
    def post(self):
        form = SettingForm(self.request.arguments, locale_code=self.locale.code)
        currentUser = self.current_user
        user = User.query.filter_by(id=currentUser.id).first()
        if form.password.data is not None:
            if form.password.data != form.confirmPassword.data :
                self.writeFailedResult()
            m = hashlib.md5()
            m.update(('%s%s%s'%(options.salt, 
                               form.email.data, 
                               form.password.data)).encode('utf-8'))
            password_md5 = m.hexdigest()
            user.password = password_md5 

        user.email = form.email.data
        user.name = form.name.data
        user.nickName = form.nickName.data
        db.session.add(user)
        db.session.commit()
        self.writeSuccessResult(user, successUrl='/')

class PeopleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        currentUser = self.current_user
        teamId = self.session["currentTeamId"]
        team = Team.query.filter_by(id=teamId).first()
        self.render("user/peoples.html", currentUser= currentUser, team= team)

class NewPeopleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("user/newPeople.html")

handlers = [
    ('/login', LoginHandler),
    ('/settings', SettingHandler),
    ('/people', PeopleHandler),
    ('/people/new', NewPeopleHandler),
]
