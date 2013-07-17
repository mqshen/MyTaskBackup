'''
Created on Feb 4, 2013

@author: GoldRatio
'''

from tornado.options import options
from forms import Form, TextField, ListField, IntField, BooleanField
from core.BaseHandler import BaseHandler 
from mysolr import Solr
import tornado

class AutoCompleteForm(Form):
    token = TextField('token')

class AutoCompleteHandler(BaseHandler):
    _error_message = "项目已存在"
    @tornado.web.authenticated
    def get(self):
        form = AutoCompleteForm(self.request.arguments, locale_code=self.locale.code)
        solr = Solr(base_url= options.solr_url)
        query = {'q' : 'title:%s'%form.token.data, 'facet' : 'true'}
        response = solr.search(**query)
        
        self.writeSuccessResult(response.documents)

