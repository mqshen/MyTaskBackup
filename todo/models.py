'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from core.database import db
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from attachment.models import Attachment


__all__ = ['TodoList', 'TodoItem']

class TodoList(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    description = Column(String(100))
    own_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    team_id = Column(Integer, ForeignKey('team.id'))
    createTime = Column(DateTime)

    todoItems = relationship("TodoItem", backref="todolist")

class TodoItem(db.Model):
    eagerRelation = ['worker']
    id = Column(Integer, primary_key=True)
    description = Column(String(300))
    own_id = Column(Integer, ForeignKey('user.id'))
    todolist_id = Column(Integer, ForeignKey('todolist.id'))
    worker_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    team_id = Column(Integer, ForeignKey('team.id'))
    deadline = Column(DateTime)
    done = Column(Integer, default=0)
    createTime = Column(DateTime)

    comments = relationship("TodoComment", backref="todoitem")

attachment_todocomment_rel = Table('attachment_todocomment_rel', db.Model.metadata,
    Column('attachment_id', Integer, ForeignKey('attachment.id')),
    Column('todocomment_id', Integer, ForeignKey('todocomment.id'))
)

class TodoComment(db.Model):
    eagerRelation = ['attachments', 'own']
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    own_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    todoitem_id = Column(Integer, ForeignKey('todoitem.id'))
    team_id = Column(Integer, ForeignKey('team.id'))
    createTime = Column(DateTime)

    attachments = relationship("Attachment", secondary=attachment_todocomment_rel , backref="todocomment")
