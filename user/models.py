'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from core.database import db
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship

__all__ = ['User', 'Team']

team_user_rel = Table('team_user_rel', db.Model.metadata,
    Column('team_id', Integer, ForeignKey('team.id')),
    Column('user_id', Integer, ForeignKey('user.id'))
)

class Team(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(30))
    createTime = Column(DateTime)

    members = relationship("User", secondary=team_user_rel, backref="teams")

class User(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    nickName = Column(String(30))
    email = Column(String(60), index=True)
    password = Column(String(60))
    description = Column(String(100))
    avatar = Column(String(60))

    ownedProjects = relationship("Project", backref="own")
    ownedMessages = relationship("Message", backref="own")
    todoItems = relationship("TodoItem", primaryjoin="User.id == TodoItem.worker_id", backref="worker")
