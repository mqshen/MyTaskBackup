import tornado.web
from core.session import Session

from core.escape import json_encode
from core.util import serialize
from user.models import User
from core.database import db


successJson = {"returnCode": "000000"}

class BaseHandler(tornado.web.RequestHandler):
    
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

    @property
    def session(self):
        sessionid = self.get_secure_cookie('sid')
        return Session(self.application.session_store, sessionid)

    def get_current_user(self):
        return self.session['user'] if self.session and 'user' in self.session else None
    
    def rawRender(self, templateName, **kwargs):
        super().render(templateName, **kwargs)

    def render(self, templateName, **kwargs):
        currentUserId = self.current_user
        user = User.query.filter_by(id=currentUserId).first()
        super().render(templateName, currentUser=user , **kwargs)
    
    def writeSuccessResult(self, model=None, **kwargs):
        result = None
        if model is not None:
            if isinstance(model, list):
                result = {"content": [serialize(item) for item in model]}
            else:
                result = serialize(model)
        else:
            result = {}
        result.update(successJson)
        for key in kwargs:
            item = kwargs[key]
            if item is not None:
                if isinstance(item, db.Model):
                    result.update({key : serialize(item)})
                else:
                    result.update({key : item})
        self.write(json_encode(result))
    
    def writeFailedResult(self):
        self.write(json_encode({"returnCode": "999999", "errorMessage": self._error_message}))

