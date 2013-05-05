import tornado.web
from core.session import Session

from core.escape import json_encode
from core.util import serialize


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
    
    def writeSuccessResult(self, model, successUrl=None):
        result = serialize(model)
        result.update(successJson)
        if successUrl is not None:
            result.update({"successUrl" : successUrl})
        self.write(json_encode(result))
    
    def writeFailedResult(self):
        self.write(json_encode({"returnCode": "999999", "errorMessage": self._error_message}))

