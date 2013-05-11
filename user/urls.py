'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from .models import User, Team, InviteProject, InviteUser
from todo.models import TodoItem
import logging
import tornado
from tornado.options import options
from tornado.web import RequestHandler
import hashlib
from core.BaseHandler import BaseHandler 
from forms import Form, TextField, ListField
from core.database import db
from core.quemail import QueMail, Email
from core.util import getSequence 
from uuid import uuid4
from datetime import datetime

class SigninForm(Form):
    email = TextField('email')
    password = TextField('password')

class RegisterForm(Form):
    email = TextField('email')
    name = TextField('name')
    teamTitle = TextField('teamTitle')
    password = TextField('password')

class TeamAccessForm(Form):
    canCreateProjects = TextField('canCreateProjects')
    admin = TextField('admin')
    email = ListField('email')
    project = ListField('project')


class RegisterHandler(BaseHandler):
    def get(self):
        self.render("register.html")

    def post(self):
        form = RegisterForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None:
                self.render("register.html", form = form, errorMessage = self._error_message)
                return
            m = hashlib.md5()
            m.update(('%s%s%s'%(options.salt, 
                               form.email.data, 
                               form.password.data)).encode('utf-8'))
            password_md5 = m.hexdigest()
            user = User(email=form.email.data, password=password_md5, name=form.name.data, nickName=form.name.data, avatar='default')
            team = Team(title=form.teamTitle.data, createTime=datetime.now(), members=[user])
            db.session.add(team)
            db.session.commit()
            self.set_secure_cookie("sid", self.session.sessionid)
            self.session["user"] = user.id 
            self.session["currentTeamId"] = team.id
            self.redirect("/")

class LoginHandler(BaseHandler):
    _error_message = "email or password incorrect!"
    def get(self):
        self.rawRender("login.html")

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
            self.session["user"] = currentUser.id
            if len(currentUser.teams) == 1:
                self.session["currentTeamId"] = currentUser.teams[0].id
                self.redirect("/")
            else:
                self.rawRender("teamSelect.html", currentUser=currentUser)

class TeamHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, teamId):
        self.session["currentTeamId"] = teamId
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
        self.render("settings/user.html") 

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
        self.render("user/peoples.html", team= team)

    @tornado.web.authenticated
    def post(self):
        teamId = self.session["currentTeamId"]
        team = Team.query.filter_by(id=teamId).first()
        currentUser = self.current_user
        qm = QueMail.get_instance()
        form = TeamAccessForm(self.request.arguments, locale_code=self.locale.code)

        inviteId = getSequence('team_invite_id')
        for projectId in form.project.data:
            inviteProject = InviteProject(invite_id= inviteId, project_id= projectId) 
            db.session.add(inviteProject)

        subject = "%s邀请您加入%s"%(currentUser.name, team.title)
        for email in form.email.data :
            hashCode = uuid4().hex
            user = db.session.execute("select user.* from user, team_user_rel where id=user_id and team_id=:teamId and email=:email", 
                    {"teamId":teamId, "email": email}).first()
            if user is not None:
                continue
            inviteUser = InviteUser(id= hashCode, email=email, invite_id=inviteId, team_id = teamId)
            db.session.add(inviteUser)
            html = self.render_string("email/invite.html", team=team, currentUser=currentUser, inviteUser=inviteUser)
            qm.send(Email(subject= subject, text= html, adr_to= email, adr_from= options.smtp.get("user")))

        db.session.commit()
        self.writeSuccessResult(successUrl='/people')

class NewPeopleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        teamId = self.session["currentTeamId"]
        team = Team.query.filter_by(id=teamId).first()
        self.render("user/newPeople.html", team=  team)

class PeopleDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userId):
        teamId = self.session["currentTeamId"]
        user = User.query.filter_by(id=userId).first()
        team = Team.query.filter_by(id=teamId).first()
        todoItems = TodoItem.query.filter_by(team_id=teamId, worker_id=user.id).all()
        self.render("user/peopleDetail.html", user=user, team=team, todoItems= todoItems)



handlers = [
    ('/register', RegisterHandler),
    ('/login', LoginHandler),
    ('/team/([0-9]+)', TeamHandler),
    ('/settings', SettingHandler),
    ('/people', PeopleHandler),
    ('/people/new', NewPeopleHandler),
    ('/people/([0-9]+)', PeopleDetailHandler),
]
