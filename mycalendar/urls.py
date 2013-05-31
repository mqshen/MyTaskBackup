'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from .models import Calendar 
from operation.models import Operation
from project.models import Project 
from todo.models import TodoList, TodoItem
from user.models import Team, User
import logging
import tornado
from tornado.options import options
from core.BaseHandler import BaseHandler 
from forms import Form, TextField, ListField, IntField, DateField
from datetime import datetime
from core.database import db
import json

class EventForm(Form):
    start_date = TextField('start_date')
    end_date = TextField('end_date')

class CalendarForm(Form):
    id = TextField('id')
    title = TextField('title')
    color = TextField('color')
    member = ListField('member')

class CalendarHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        currentUser = self.current_user
        teamId = currentUser.teamId 
        projects = Project.query.join(Project.users).filter(User.id==currentUser.id, Project.team_id==teamId).all()
        calendars = Calendar.query.join(Calendar.users).filter(User.id==currentUser.id, Calendar.team_id==teamId).all()
        team = Team.query.filter_by(id=teamId).first()
        self.render("calendar/calendar.html", projects= projects, calendars= calendars , team = team)

    @tornado.web.authenticated
    def post(self):
        currentUser = self.current_user
        teamId = currentUser.teamId 
        form = CalendarForm(self.request.arguments, locale_code=self.locale.code)
        if form.id.data :
            calendar = Calendar.query.filter_by(id=form.id.data).first()
            calendar.color = form.color.data
            calendar.title = form.title.data
        else:
            calendar = Calendar.query.filter_by(title=form.title.data, team_id=teamId).first()
            if calendar:
                self.writeFailedResult()
                self.finish()
                return

            users = []

            user = User.query.filter_by(id=currentUser.id).first()
            users.append(user)

            for userId in form.member.data:
                users.append(User.query.filter_by(id=userId).first())

            now = datetime.now()
            calendar = Calendar(title=form.title.data, color=form.color.data, own_id=currentUser.id, team_id=teamId, createTime= now, users = users)
        db.session.add(calendar)

        db.session.commit()
        
        self.writeSuccessResult(calendar)


class CalendarEventHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        form = EventForm(self.request.arguments, locale_code=self.locale.code)
        currentUser = self.current_user
        teamId = currentUser.teamId 
        todoItems = TodoItem.query.filter(TodoItem.team_id==teamId, TodoItem.worker_id == currentUser.id, TodoItem.deadline >= form.start_date.data, TodoItem.deadline <= form.end_date.data).all()
        self.writeSuccessResult(todoItems = todoItems )

handlers = [
    ('/calendar', CalendarHandler),
    ('/fetchEvent', CalendarEventHandler),
]
