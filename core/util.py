'''
Created on May 2, 2013

@author: GoldRatio
'''
from sqlalchemy.orm import class_mapper
from tornado.options import options

def serialize(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    return dict((c, getattr(model, c)) for c in columns if c not in options.jsonFilter)
