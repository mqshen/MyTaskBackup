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
from core.html2text import html2text
from websocket.urls import send_message
import core.web


class MessageForm(Form):
    title = TextField('title')
    content = TextField('content')
    attachment = ListField('attachment')
    attachmentDel = ListField('attachmentDel')

class CommentForm(Form):
    content = TextField('content')
    attachment = ListField('attachment')
    attachmentDel = ListField('attachmentDel')


class MessageHandler(BaseHandler):
    _error_message = "email or password incorrect!"
    @tornado.web.authenticated
    def get(self, projectId):
        project = Project.query.filter_by(id=projectId).first()
        self.render("topic/messages.html", project= project)

    @tornado.web.authenticated
    def post(self, projectId):
        form = MessageForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            currentUser = self.current_user
            teamId = currentUser.teamId
            now = datetime.now()
            digest = html2text(form.content.data)

            message = Message(title=form.title.data, content=form.content.data, 
                own_id=currentUser.id, project_id= projectId, team_id=teamId, comment_digest= digest, attachments=[])

            for attachment in form.attachment.data:
                attachment = Attachment.query.filter_by(url=attachment).first()
                if attachment is not None:
                    message.attachments.append(attachment)

            db.session.add(message)
            db.session.flush()
            messageId = message.id

            url = "/project/%s/message/%d"%(projectId, message.id)
            operation = Operation(own_id = currentUser.id, createTime= now, operation_type=1, target_type=1,
                target_id=messageId, title= message.title, team_id= teamId, project_id= projectId, url= url)
            db.session.add(operation)

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

        for url in form.attachmentDel.data:
            for attachment in message.attachments:
                if attachment.url == url:
                    message.attachments.remove(attachment)

        for attachment in form.attachment.data:
            attachment = Attachment.query.filter_by(url=attachment).first()
            if attachment is not None:
                attachment.project_id = projectId
                attachment.team_id = teamId
                message.attachments.append(attachment)
                
        db.session.add(message)
        db.session.commit()
        self.writeSuccessResult(message)

class CommentDetailHandler(BaseHandler):
    @tornado.web.authenticated
    @core.web.authenticatedProject
    def get(self, projectId, messageId, commentId):
        project = Project.query.filter_by(id=projectId).first()
        message = Message.query.filter_by(id=messageId).first()
        currentUser = self.current_user
        self.render("topic/messageDetail.html", project= project, message= message)

    @tornado.web.authenticated
    @core.web.authenticatedProject
    def post(self, projectId, messageId, commentId, **kwargs):
        form = MessageForm(self.request.arguments, locale_code=self.locale.code)
        message = Message.query.filter_by(id=messageId).first()
        comment = Comment.query.filter_by(id=commentId).first()
        currentUser = self.current_user
        teamId = currentUser.teamId
        now = datetime.now()
        comment.content = form.content.data
        commentId = comment.id

        url = "/project/%s/message/%s/comment/%d"%(projectId, messageId, commentId)
        operation = Operation(own_id = currentUser.id, createTime= now, operation_type=4, target_type=2,
            target_id=messageId, title= message.title, digest=comment.content, team_id= teamId, project_id= projectId, url= url)

        db.session.add(operation)

        for attachment in form.attachment.data:
            attachment = Attachment.query.filter_by(url=attachment).first()
            if attachment is not None:
                attachment.project_id = projectId
                attachment.team_id = teamId
                db.session.add(attachment)
                
        for url in form.attachmentDel.data:
            for attachment in message.attachments:
                if attachment.url == url:
                    comment.attachments.remove(attachment)

        db.session.add(comment)
        db.session.commit()
        self.writeSuccessResult(comment)

class CommentHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, projectId, messageId):
        form = CommentForm(self.request.arguments, locale_code=self.locale.code)
        if form.validate():
            currentUser = self.current_user
            teamId = currentUser.teamId
            message = Message.query.filter_by(id=messageId).with_lockmode("update").first()
            now = datetime.now()
            comment = Comment(content=form.content.data, message_id=messageId ,
                own_id=currentUser.id, project_id= projectId, team_id=teamId, createTime= now)
            db.session.add(comment)
            db.session.flush()
            commentId = comment.id
            digest = html2text(form.content.data)

            message.comment_num = message.comment_num + 1
            message.comment_digest = digest

            db.session.add(message)

            url = "/project/%s/message/%s/comment/%d"%(projectId, messageId, commentId)

            operation = Operation(own_id = currentUser.id, createTime= now, operation_type=2, target_type=1,
                target_id=messageId, title= message.title, digest= digest, team_id= teamId, project_id= projectId, url= url)

            db.session.add(operation)

            for attachment in form.attachment.data:
                attachment = Attachment.query.filter_by(url=attachment).first()
                if attachment is not None:
                    attachment.project_id = projectId
                    attachment.team_id = teamId
                    db.session.add(attachment)
            db.session.commit()
            send_message(currentUser.id, teamId, 2, 1, comment)

            self.writeSuccessResult(comment)

handlers = [
    ('/project/([0-9]+)/message', MessageHandler),
    ('/project/([0-9]+)/message/([0-9]+)', MessageDetailHandler),
    ('/project/([0-9]+)/message/new', NewMessageHandler),
    ('/project/([0-9]+)/message/([0-9]+)/comment', CommentHandler),
    ('/project/([0-9]+)/message/([0-9]+)/comment/([0-9]+)', CommentDetailHandler),
]
