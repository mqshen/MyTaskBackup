'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from .models import TodoList, TodoItem
from attachment.models import Attachment
from project.models import Project
import logging
import tornado
from tornado.options import options
from tornado.web import RequestHandler
from core.BaseHandler import BaseHandler 
from forms import Form, TextField, ListField
from datetime import datetime
from core.database import db


class MessageForm(Form):
    title = TextField('title')
    content = TextField('content')
    attachment = ListField('attachment')

class TodoListForm(Form):
    title = TextField('title')

class TodoListHandler(BaseHandler):
    _error_message = "email or password incorrect!"

    @tornado.web.authenticated
    def get(self, projectId):
        self.render("topic/message.html", projectId= projectId)

    @tornado.web.authenticated
    def post(self, projectId):
        form = TodoListForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            teamId = self.session["currentTeamId"]
            currentUser = self.current_user
            todoList = TodoList(title=form.title.data, 
                own_id=currentUser.id, project_id= projectId, team_id=teamId, createTime=datetime.now())
            db.session.add(todoList)
            db.session.commit()
            self.writeSuccessResult(todoList)

handlers = [
    ('/project/([0-9]+)/todolist', TodoListHandler),
]
