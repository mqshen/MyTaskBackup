'''
Created on Feb 4, 2013

@author: GoldRatio
'''
from core.database import db
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship


__all__ = ['Calendar'] 

class Calendar(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    description = Column(String(60))

