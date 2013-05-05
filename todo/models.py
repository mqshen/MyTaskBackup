'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from core.database import db
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship


__all__ = ['TodoList']

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
    id = Column(Integer, primary_key=True)
    description = Column(String(300))
    own_id = Column(Integer, ForeignKey('user.id'))
    todolist_id = Column(Integer, ForeignKey('todolist.id'))
    worker_id = Column(Integer, ForeignKey('user.id'))
    deadline = Column(DateTime)
    createTime = Column(DateTime)
    
