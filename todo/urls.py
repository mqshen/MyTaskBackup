'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from user.models import User
from .models import TodoList, TodoItem
from attachment.models import Attachment
from project.models import Project
import logging
import tornado
from tornado.options import options
from tornado.web import RequestHandler
from core.BaseHandler import BaseHandler 
from forms import Form, TextField, ListField, IntField, DateField
from datetime import datetime
from core.database import db


class TodoItemForm(Form):
    description = TextField('description')
    workerId = IntField('workerId')
    deadLine = DateField("deadLine")

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

class TodoItemHandler(BaseHandler):
    _error_message = ""

    @tornado.web.authenticated
    def post(self, projectId, todoListId):
        form = TodoItemForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            teamId = self.session["currentTeamId"]
            currentUser = self.current_user
            todoItem = TodoItem(description=form.description.data, 
                own_id=currentUser.id, todolist_id= todoListId, project_id= projectId, worker_id= form.workerId.data,
                deadline= form.deadLine.data, team_id=teamId, createTime=datetime.now())
            db.session.add(todoItem)
            db.session.commit()
            worker = None
            if todoItem.worker_id is not None:
                worker = User.query.filter_by(id=todoItem.worker_id).first()
            self.writeSuccessResult(todoItem, worker=worker)

class TodoItemDetailHandler(BaseHandler):
    _error_message = ""

    @tornado.web.authenticated
    def post(self, projectId, todoListId, todoItemId):
        form = TodoItemForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            teamId = self.session["currentTeamId"]
            currentUser = self.current_user
            todoItem = TodoItem.query.filter_by(id=todoItemId).first()
            if todoItem is not None:
                todoItem.worker_id = form.workerId.data
                todoItem.deadline = form.deadLine.data
                if len(form.description.data) > 0 :
                    todoItem.description = form.description.data
                    
                db.session.add(todoItem)
                db.session.commit()
                worker = None
                if todoItem.worker_id is not None:
                    worker = User.query.filter_by(id=todoItem.worker_id).first()
                self.writeSuccessResult(todoItem, worker=worker)

class TodoItemModifyHandler(BaseHandler):
    _error_message = ""

    @tornado.web.authenticated
    def post(self, projectId, todoListId, todoItemId, operation):
        todoItem = TodoItem.query.filter_by(id=todoItemId).first()
        if operation == "trash" :
            db.session.delete(todoItem)
            db.session.commit()

        self.writeSuccessResult(todoItem)

handlers = [
    ('/project/([0-9]+)/todolist', TodoListHandler),
    ('/project/([0-9]+)/todolist/([0-9]+)/todoitem', TodoItemHandler),
    ('/project/([0-9]+)/todolist/([0-9]+)/todoitem/([0-9]+)', TodoItemDetailHandler),
    ('/project/([0-9]+)/todolist/([0-9]+)/todoitem/([0-9]+)/([a-zA-Z]+)', TodoItemModifyHandler),
]
