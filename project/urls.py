'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from .models import Project
from topic.models import Message 
from todo.models import TodoList
from user.models import Team, User
import logging
import tornado
from tornado.options import options
from core.BaseHandler import BaseHandler 
from forms import Form, TextField, ListField
from datetime import datetime
from core.database import db
import json


class ProjectForm(Form):
    name = TextField('name')
    description = TextField('description')
    member = ListField('member')

class ProjectHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        teamId = self.session["currentTeamId"]
        projects = Project.query.filter_by(team_id=teamId).all()
        self.render("project/project.html", projects= projects)

    @tornado.web.authenticated
    def post(self):
        teamId = self.session["currentTeamId"]
        form = ProjectForm(self.request.arguments, locale_code=self.locale.code)
        currentUser = self.current_user
        
        users = []
        for userId in form.member.data:
            users.append(User.query.filter_by(id=userId).first())

        project = Project(title=form.name.data, description=form.description.data, 
                own_id=currentUser.id, team_id=teamId, createTime=datetime.now(), users = users)
        db.session.add(project)
        db.session.flush()


        db.session.commit()
        self.writeSuccessResult(project, successUrl='/')


class NewProjectHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        teamId = self.session["currentTeamId"]
        team = Team.query.filter_by(id=teamId).first()
        self.render("project/newProject.html", team= team)

    @tornado.web.authenticated
    def post(self):
        self.redirect("/")

class ProjectDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, projectId):
        project = Project.query.filter_by(id=projectId).first()
        messages = Message.query.filter_by(project_id=projectId).order_by(Message.createTime).limit(5).all()
        todolists = TodoList.query.filter_by(project_id=projectId).all()
        self.render("project/projectDetail.html", project= project, messages= messages, todolists= todolists)


handlers = [
    ('/', ProjectHandler),
    ('/project', ProjectHandler),
    ('/project/([0-9]+)', ProjectDetailHandler),
    ('/project/new', NewProjectHandler),
]
