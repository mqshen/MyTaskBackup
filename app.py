import tornado.ioloop
import tornado.web
import os.path
import redis
from core.session import RedisSessionStore
from tornado.options import options
from core.urlResolver import urlResolver
from core.quemail import QueMail

class Application(tornado.web.Application):
    def __init__(self, settings):
        handlers = urlResolver().resolverUrls()
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        r = redis.Redis(connection_pool=pool)
        self.session_store = RedisSessionStore(r)
        tornado.web.Application.__init__(self, handlers, **settings)
        
        qm = QueMail.get_instance()
        qm.init(options.smtp.get("host"), options.smtp.get("user"), options.smtp.get("password"))
        qm.start()

    def __del__(self):
        qm = QueMail.get_instance()
        qm.end()

def main():
    options.parse_config_file("conf/config.conf")

    settings = dict(
        cookie_secret = "__TODO:_Generate_your_own_random_value_here__",
        template_path = os.path.join(os.path.dirname(__file__), options.templatesPath),
        static_path = os.path.join(os.path.dirname(__file__), options.staticPath),
        xsrf_cookies = False,
        autoescape = None,
        debug = True,
        login_url = options.login_url,
    )
    app = Application(settings)
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
