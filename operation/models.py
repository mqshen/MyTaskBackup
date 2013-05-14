'''
Created on Feb 4, 2013

    operation_type = Column(Enum('创建', '发起', '回复', '删除', '编辑', '查询', '回复', '开始', '暂停', '完成', '取消完成'))
    target_type = Column(Enum('项目', '讨论', '评论', '任务列表', '任务', '用户'))
@author: GoldRatio
'''
from core.database import db
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship

__all__ = ['Operation']

class Operation(db.Model):
    eagerRelation = ["own", "project"]
    id = Column(Integer, primary_key=True)
    own_id = Column(Integer, ForeignKey('user.id'))
    createTime = Column(DateTime)
    operation_type = Column(Integer(2))
    target_type = Column(Integer(2))
    target_id = Column(Integer)
    title = Column(String(100))
    url = Column(String(100))
    digest = Column(String(200))
    team_id = Column(Integer)
    project_id = Column(Integer, ForeignKey('project.id'))


