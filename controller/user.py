'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from model.user import User, Team, InviteProject, InviteUser, UserObj, TeamUserRel, Cookie
from model.todo import TodoItem
import logging
import tornado
from tornado.options import options
from tornado.web import RequestHandler
from tornado.web import HTTPError
import hashlib
from core.BaseHandler import BaseHandler 
from forms import Form, TextField, ListField, BooleanField
from core.database import db
from core.quemail import QueMail, Email
from core.util import getSequence 
import core.web
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

class TeamForm(Form):
    teamTitle = TextField('teamTitle')

class TeamAccessForm(Form):
    create = BooleanField('create')
    admin = BooleanField('admin')
    email = ListField('email')
    projectId = ListField('projectId')

class JoinForm(Form):
    email = TextField('email')
    name = TextField('name')
    password = TextField('password')


class RegisterHandler(BaseHandler):
    _error_message = "用户名已存在"
    def get(self):
        self.rawRender("register.html")

    def post(self):
        form = RegisterForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None:
                self.rawRender("register.html", form = form, errorMessage = self._error_message)
                return
            m = hashlib.md5()
            m.update(('%s%s%s'%(options.salt, 
                               form.email.data, 
                               form.password.data)).encode('utf-8'))
            password_md5 = m.hexdigest()
            user = User(email=form.email.data, password=password_md5, name=form.name.data, nickName=form.name.data, avatar='default')
            team = Team(title=form.teamTitle.data, createTime=datetime.now())

            teamUserRel = TeamUserRel(privilege=2, member=user, team=team)

            db.session.add(teamUserRel)
            db.session.commit()
            self.set_secure_cookie("sid", self.session.sessionid)
            self.session["user"] = UserObj(user, team.id)
            self.redirect("/")

class LoginHandler(BaseHandler):
    _error_message = "email or password incorrect!"
    def get(self):
        sessionid = self.get_secure_cookie('sid')
        cookie = Cookie.query.filter_by(sid= sessionid).first()
        nextUrl = self.get_argument("next", None, True)
        if cookie and cookie.user:
            currentUser = cookie.user
            self.set_secure_cookie("sid", self.session.sessionid)
            if len(currentUser.teams) == 1:
                self.session["user"] = UserObj(currentUser, currentUser.teams[0].id)
                self.redirect("/")
            else:
                self.session["user"] = UserObj(currentUser)
                self.session._save()
                self.rawRender("teamSelect.html", currentUser=currentUser, nextUrl=nextUrl)
            return
        self.rawRender("login.html", nextUrl=nextUrl)

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

            cookie = Cookie.query.filter_by(user_id = currentUser.id).first()
            if cookie:
                cookie.sid = self.session.sessionid
            else:
                cookie = Cookie(user_id= currentUser.id, sid= self.session.sessionid)
            db.session.add(cookie)
            db.session.commit()

            if len(currentUser.teams) == 1:
                self.session["user"] = UserObj(currentUser, currentUser.teams[0].id)
                self.redirect("/")
            else:
                self.session["user"] = UserObj(currentUser)
                self.session._save()
                self.rawRender("teamSelect.html", currentUser=currentUser)

class TeamHandler(BaseHandler):
    @tornado.web.authenticated
    @core.web.authenticatedTeam
    def get(self, teamId):
        currentUser = self.current_user
        currentUser.teamId = int(teamId)
        self.session["user"] = currentUser
        self.redirect("/")

class TeamNewHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        currentUser = self.current_user
        self.rawRender("teamSelect.html", currentUser=currentUser)

    @tornado.web.authenticated
    def post(self):
        form = TeamForm(self.request.arguments, locale_code=self.locale.code)
        currentUser = self.current_user
        user = User.query.filter_by(id=currentUser.id).first()
        team = Team(title=form.teamTitle.data, createTime=datetime.now())
        teamUserRel = TeamUserRel(member= user, team=team, privilege=2)

        db.session.add(teamUserRel)
        db.session.commit()

        currentUser.teamId = team.id 
        self.session["user"] = currentUser
        self.writeSuccessResult(team, successUrl='/')


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
                self.finish()
                return
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
        currentUser.email = user.email
        currentUser.name = user.name
        currentUser.nickName = user.nickName
        self.session["user"] = currentUser

        self.writeSuccessResult(user, successUrl='/')

class PeopleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        teamId = self.current_user.teamId
        team = Team.query.filter_by(id=teamId).first()
        self.render("user/peoples.html", team= team)

    @tornado.web.authenticated
    def post(self):
        currentUser = self.current_user
        teamId = currentUser.teamId
        team = Team.query.filter_by(id=teamId).first()
        qm = QueMail.get_instance()
        form = TeamAccessForm(self.request.arguments, locale_code=self.locale.code)

        inviteId = getSequence('team_invite_id')
        for projectId in form.projectId.data:
            inviteProject = InviteProject(invite_id= inviteId, project_id= projectId) 
            db.session.add(inviteProject)

        subject = "%s邀请您加入%s"%(currentUser.name, team.title)
        for email in form.email.data :
            hashCode = uuid4().hex
            user = db.session.execute("select user.* from user, team_user_rel where id=user_id and team_id=:teamId and email=:email", 
                    {"teamId":teamId, "email": email}).first()
            if user is not None:
                continue
            inviteUser = InviteUser.query.filter_by(email= email).first()
            if inviteUser:
                continue
            privilege = 0
            if form.create.data :
                privilege = 1
            if form.admin.data :
                privilege = 2
            inviteUser = InviteUser(id= hashCode, email=email, invite_id=inviteId, team_id = teamId, privilege= privilege)
            db.session.add(inviteUser)
            html = self.render_string("email/invite.html", team=team, currentUser=currentUser, inviteUser=inviteUser)
            qm.send(Email(subject= subject, text= html, adr_to= email, adr_from= options.smtp.get("user")))

        db.session.commit()
        self.writeSuccessResult(successUrl='/people')

class NewPeopleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        teamId = self.current_user.teamId
        team = Team.query.filter_by(id=teamId).first()
        self.render("user/newPeople.html", team=  team)

class PeopleDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userId):
        teamId = self.current_user.teamId
        user = User.query.filter_by(id=userId).first()
        team = Team.query.filter_by(id=teamId).first()
        todoItems = TodoItem.query.filter_by(team_id=teamId, worker_id=user.id, done=0).all()
        self.render("user/peopleDetail.html", user=user, team=team, todoItems= todoItems)


class JoinHandler(BaseHandler):
    def get(self, hashCode):
        inviteUser = InviteUser.query.filter_by(id=hashCode).first()
        if not inviteUser:
            raise HTTPError(404)
        user = User.query.filter_by(email=inviteUser.email).first()
        if user :
            inviteProjects = InviteProject.query.filter_by(invite_id=inviteUser.invite_id).all()
            db.session.execute("insert into team_user_rel values(:teamId, :userId, :privilege)", 
                    {"teamId": inviteUser.team_id, "userId": user.id, "privilege": inviteUser.privilege})
            for inviteProject in inviteProjects:
                db.session.execute("insert into project_user_rel values(:projectId, :userId)", {"projectId": inviteProject.project_id, "userId": user.id})
            db.session.delete(inviteUser)
            db.session.commit()

            self.session["user"] = UserObj(user, inviteUser.team_id)
            self.redirect("/")
        else:
            self.render("user/join.html", user=inviteUser)

    def post(self, hashCode):
        inviteUser = InviteUser.query.filter_by(id=hashCode).first()
        inviteProjects = InviteProject.query.filter_by(invite_id= inviteUser.invite_id).all()
        form = JoinForm(self.request.arguments, locale_code=self.locale.code)
        m = hashlib.md5()
        m.update(('%s%s%s'%(options.salt, 
                           form.email.data, 
                           form.password.data)).encode('utf-8'))
        password_md5 = m.hexdigest()
        user = User(email= inviteUser.email, name= form.name.data, password= password_md5, nickName=form.name.data, avatar="default")
        db.session.add(user)
        db.session.flush()
        db.session.execute("insert into team_user_rel values(:teamId, :userId, :privilege)", 
                    {"teamId": inviteUser.team_id, "userId": user.id, "privilege": inviteUser.privilege})
        for inviteProject in inviteProjects:
            db.session.execute("insert into project_user_rel values(:projectId, :userId)", {"projectId": inviteProject.project_id, "userId": user.id})
        db.session.delete(inviteUser)
        db.session.commit()

        self.session["user"] = UserObj(user, inviteUser.team_id)
        self.redirect("/")


class SignOutHandler(BaseHandler):
    _error_message = "email or password incorrect!"
    def get(self):
        self.post()

    def post(self):
        self.session.clear()
        self.redirect("/")
