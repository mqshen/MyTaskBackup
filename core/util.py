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
    result = dict((c, getattr(model, c)) for c in columns if c not in options.jsonFilter)
    if hasattr(model, 'eagerRelation'):
        for key in model.eagerRelation:
            result.update({key: serialize(getattr(model, key))})
        columns.extend(model.eagerRelation)
    # then we return their values in a dict
    
    return result
