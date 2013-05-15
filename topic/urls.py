'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from .models import Message, Comment
from operation.models import Operation
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
import core.web


class MessageForm(Form):
    title = TextField('title')
    content = TextField('content')
    attachment = ListField('attachment')
    attachmentDel = ListField('attachmentDel')

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
            currentUser = self.current_user
            teamId = currentUser.teamId
            now = datetime.now()
            message = Message(title=form.title.data, content=form.content.data, 
                own_id=currentUser.id, project_id= projectId, team_id=teamId)
            db.session.add(message)
            db.session.flush()
            messageId = message.id

            url = "/project/%s/message/%d"%(projectId, message.id)
            operation = Operation(own_id = currentUser.id, createTime= now, operation_type=1, target_type=1,
                target_id=messageId, title= message.title, team_id= teamId, project_id= projectId, url= url)
            db.session.add(operation)

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
    @core.web.authenticatedProject
    def get(self, projectId, messageId):
        project = Project.query.filter_by(id=projectId).first()
        message = Message.query.filter_by(id=messageId).first()
        currentUser = self.current_user
        self.render("topic/messageDetail.html", project= project, message= message)

    @tornado.web.authenticated
    @core.web.authenticatedProject
    def post(self, projectId, messageId, **kwargs):
        form = MessageForm(self.request.arguments, locale_code=self.locale.code)
        project = Project.query.filter_by(id=projectId).first()
        message = Message.query.filter_by(id=messageId).first()
        currentUser = self.current_user
        teamId = currentUser.teamId
        now = datetime.now()
        message.title = form.title.data
        message.content = form.content.data
        messageId = message.id

        url = "/project/%s/message/%d"%(projectId, messageId)
        operation = Operation(own_id = currentUser.id, createTime= now, operation_type=4, target_type=1,
            target_id=messageId, title= message.title, team_id= teamId, project_id= projectId, url= url)

        db.session.add(operation)

        for attachment in form.attachment.data:
            attachment = Attachment.query.filter_by(url=attachment).first()
            if attachment is not None:
                attachment.project_id = projectId
                attachment.message_id = messageId
                attachment.team_id = teamId
                db.session.add(attachment)
                
        for url in form.attachmentDel.data:
            for attachment in message.attachments:
                if attachment.url == url:
                    message.attachments.remove(attachment)

        db.session.add(message)
        db.session.commit()
        self.writeSuccessResult(message)

class CommentHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, projectId, messageId):
        form = CommentForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            currentUser = self.current_user
            teamId = currentUser.teamId
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
