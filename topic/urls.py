'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from .models import Message, Comment
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

class CommentForm(Form):
    content = TextField('content')

class MessageHandler(BaseHandler):
    _error_message = "email or password incorrect!"
    @tornado.web.authenticated
    def get(self, projectId):
        self.render("topic/message.html", projectId= projectId)

    @tornado.web.authenticated
    def post(self, projectId):
        form = MessageForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            teamId = self.session["currentTeamId"]
            currentUser = self.current_user
            message = Message(title=form.title.data, content=form.content.data, 
                own_id=currentUser.id, project_id= projectId, team_id=teamId, createTime=datetime.now())
            db.session.add(message)
            db.session.flush()
            messageId = message.id
            for attachment in form.attachment.data:
                attachment = Attachment.query.filter_by(url=attachment).first()
                if attachment is not None:
                    attachment.project_id = projectId
                    attachment.message_id = messageId
                    attachment.team_id = teamId
                    db.session.add(attachment)
            db.session.commit()
            self.writeSuccessResult(message, successUrl='/project/%s/message/%d'%(projectId, message.id))


class NewMessageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, projectId):
        project = Project.query.filter_by(id=projectId).first()
        self.render("topic/newMessage.html", project= project)

class MessageDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, projectId, messageId):
        project = Project.query.filter_by(id=projectId).first()
        message = Message.query.filter_by(id=messageId).first()
        currentUser = self.current_user
        self.render("topic/messageDetail.html", project= project, message= message, currentUser= currentUser)

class CommentHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, projectId, messageId):
        form = CommentForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            teamId = self.session["currentTeamId"]
            currentUser = self.current_user
            comment = Comment(content=form.content.data, message_id=messageId ,
                own_id=currentUser.id, project_id= projectId, team_id=teamId, createTime=datetime.now())
            db.session.add(comment)
            db.session.commit()
            self.writeSuccessResult(comment)

handlers = [
    ('/project/([0-9]+)/message', MessageHandler),
    ('/project/([0-9]+)/message/([0-9]+)', MessageDetailHandler),
    ('/project/([0-9]+)/message/new', NewMessageHandler),
    ('/project/([0-9]+)/message/([0-9]+)/comment', CommentHandler),
]
