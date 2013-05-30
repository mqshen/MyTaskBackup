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

class CalendarHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        currentUser = self.current_user
        teamId = currentUser.teamId 
        projects = Project.query.join(Project.users).filter(User.id==currentUser.id, Project.team_id==teamId).all()
        self.render("calendar/calendar.html", projects= projects)

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
