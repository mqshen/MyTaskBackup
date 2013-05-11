'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from project.models import Project
from core.database import db
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship

__all__ = ['User', 'Team', 'InviteUser', 'InviteProject']

team_user_rel = Table('team_user_rel', db.Model.metadata,
    Column('team_id', Integer, ForeignKey('team.id')),
    Column('user_id', Integer, ForeignKey('user.id'))
)

class Team(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(30))
    createTime = Column(DateTime)

    members = relationship("User", secondary=team_user_rel, backref="teams")
    projects = relationship("Project", backref="team")
    invitedUser = relationship("InviteUser", primaryjoin="InviteUser.team_id == Team.id", backref="team")

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
    ownedOperations = relationship("Operation", backref="own")
    todoItems = relationship("TodoItem", primaryjoin="User.id == TodoItem.worker_id", backref="worker")

class InviteUser(db.Model):
    id = Column(String(60), primary_key=True)
    email = Column(String(60))
    invite_id = Column(Integer)
    team_id = Column(Integer, ForeignKey('team.id'))

class InviteProject(db.Model):
    invite_id = Column(Integer)
    project_id = Column(Integer)

