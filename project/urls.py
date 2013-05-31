'''
Created on Feb 4, 2013

@author: GoldRatio
'''
import os
from .models import Project
from operation.models import Operation
from topic.models import Message 
from todo.models import TodoList
from user.models import Team, User
import logging
import tornado
from tornado.options import options
from core.BaseHandler import BaseHandler 
import core.web 
from forms import Form, TextField, ListField, IntField, BooleanField
from datetime import datetime
from core.database import db
import json
import pinyin


class ProjectForm(Form):
    name = TextField('name')
    description = TextField('description')
    member = ListField('member')

class ProjectAccessForm(Form):
    userId = IntField('userId')
    operation = TextField('operation')

class ProjectHandler(BaseHandler):
    _error_message = "项目已存在"

    @tornado.web.authenticated
    def get(self):
        currentUser = self.current_user
        teamId = currentUser.teamId 
        projects = Project.query.join(Project.users).filter(User.id==currentUser.id, Project.team_id==teamId).all()
        self.render("project/project.html", projects= projects)

    @tornado.web.authenticated
    def post(self):
        currentUser = self.current_user
        teamId = currentUser.teamId 
        form = ProjectForm(self.request.arguments, locale_code=self.locale.code)
        
        project = Project.query.filter_by(title=form.name.data, team_id=teamId).first()
        if project :
            self.writeFailedResult()
            self.finish()
            return

        users = []

        user = User.query.filter_by(id=currentUser.id).first()
        users.append(user)

        for userId in form.member.data:
            users.append(User.query.filter_by(id=userId).first())

        now = datetime.now()
        project = Project(title=form.name.data, description=form.description.data, 
                own_id=currentUser.id, team_id=teamId, createTime= now, users = users)
        db.session.add(project)
        db.session.flush()
        needRepository = 0


        url = "/project/%d"%project.id
        operation = Operation(own_id = currentUser.id, createTime= now, operation_type=0, target_type=0, 
                target_id=project.id, title= project.title, team_id= teamId, project_id= project.id, url= url)

        db.session.add(operation)


        db.session.commit()
        
        currentUser.projects.append(project.id)
        self.session["user"] = currentUser
        self.writeSuccessResult(project, successUrl='/')


class NewProjectHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        currentUser = self.current_user
        teamId = currentUser.teamId 
        team = Team.query.filter_by(id=teamId).first()
        self.render("project/newProject.html", team= team)

    @tornado.web.authenticated
    def post(self):
        self.redirect("/")

class ProjectDetailHandler(BaseHandler):
    @tornado.web.authenticated
    @core.web.authenticatedProject
    def get(self, projectId):
        project = Project.query.filter_by(id=projectId).first()
        messages = Message.query.filter_by(project_id=projectId).order_by(Message.createTime).limit(5).all()
        todolists = TodoList.query.filter_by(project_id=projectId).all()
        self.render("project/projectDetail.html", project= project, messages= messages, todolists= todolists)


class ProjectAccessHandler(BaseHandler):
    @tornado.web.authenticated
    @core.web.authenticatedProject
    def get(self, projectId):
        project = Project.query.filter_by(id=projectId).first()
        currentUser = self.current_user
        teamId = currentUser.teamId 
        team = Team.query.filter_by(id=teamId).first()
        currentUser = self.current_user
        self.render("project/projectAccess.html", project= project, team= team)

    @tornado.web.authenticated
    @core.web.authenticatedProject
    def post(self, projectId):
        form = ProjectAccessForm(self.request.arguments, locale_code=self.locale.code)
        if(form.operation.data == "add"):
            db.session.execute("insert into project_user_rel values(:project_id, :user_id)", {"project_id":projectId, "user_id":form.userId.data})
        else:
            db.session.execute("delete from project_user_rel where project_id= :project_id and user_id = :user_id", 
                    {"project_id":projectId, "user_id":form.userId.data})

        db.session.commit()

        self.writeSuccessResult(successUrl='/')

handlers = [
    ('/', ProjectHandler),
    ('/project', ProjectHandler),
    ('/project/([0-9]+)', ProjectDetailHandler),
    ('/project/([0-9]+)/access', ProjectAccessHandler),
    ('/project/new', NewProjectHandler),
]
