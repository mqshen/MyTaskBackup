'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from .models import Calendar 
from operation.models import Operation
from topic.models import Message 
from todo.models import TodoList
from user.models import Team, User
import logging
import tornado
from tornado.options import options
from core.BaseHandler import BaseHandler 
from forms import Form, TextField, ListField, IntField
from datetime import datetime
from core.database import db
import json


class CalendarHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("calendar/calendar.html")

handlers = [
    ('/calendar', CalendarHandler),
]
