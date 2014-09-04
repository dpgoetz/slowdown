from eventlet import sleep
from time import time
import random
from swift.common.wsgi import WSGIContext
from swift.common.swob import Request
from swift.common.utils import FileLikeIter, json


def slow_iter(req, wsgi_iter, data_to_read, sleep_time):
    wsgi_iter = iter(wsgi_iter)
    bytes_read = 0
    if req.range and req.range.ranges[0][0]:
        bytes_read += req.range.ranges[0][0]
    while True:
        chunk = wsgi_iter.next()
        if bytes_read is not None and chunk:

            bytes_read += len(chunk)
            if bytes_read > data_to_read:
                sleep(sleep_time)
                bytes_read = None
        yield chunk


class _SlowDownContext(WSGIContext):
    def __init__(self, slowdown, data_to_read, sleep_time, req):
        WSGIContext.__init__(self, slowdown.app)
        self.data_to_read = data_to_read
        self.sleep_time = sleep_time
        self.req = req

    def handle_request(self, env, start_response):
        app_resp = self._app_call(env)
        app_resp = slow_iter(self.req, app_resp,
                             self.data_to_read, self.sleep_time)
        start_response(self._response_status,
                       self._response_headers,
                       self._response_exc_info)
        return app_resp


class SlowDown(object):
    """
    Some middleware that slows stuff down.

    Will so down GET and PUT requests based on a json formatted conf file.
    A sample conf looks like:

    {"slowdown_percentage": 5, "account": "all",
      "time_to_sleep": 5, "bytes_to_read": 0}


    """
    def __init__(self, app, conf):
        self.app = app
        self.data_file = conf.get('data_file', '/tmp/slowdown')
        self._slowdown_data = {}
        self.last_get = 0

    def get_slowdown_data(self):
        if time() - self.last_get > 10:
            try:
                self._slowdown_data = json.load(open(self.data_file))
            except (ValueError, IOError):
                self._slowdown_data = {}
            self.last_get = time()
        return self._slowdown_data

    def __call__(self, env, start_response):
        """
        WSGI entry point.

        :param env: WSGI environment dictionary
        :param start_response: WSGI callable
        """
        req = Request(env)

        try:
            device, partition, account, junk, junk = \
                req.split_path(3, 5, True)
        except ValueError:
            return self.app(env, start_response)

        sd_data = self.get_slowdown_data()
        data_to_read = sd_data.get('bytes_to_read', 0)
        time_to_sleep = sd_data.get('time_to_sleep', 0)
        reqs_to_slow = sd_data.get('reqs_to_slow', ['GET', 'PUT'])

        if ((account == sd_data.get('account') or
             sd_data.get('account') == 'all') and
            req.method in reqs_to_slow and
            random.random() <
                float(sd_data.get('slowdown_percentage', 0)) / 100):
            if req.method == 'GET':
                context = _SlowDownContext(
                    self, data_to_read, time_to_sleep, req)
                return context.handle_request(env, start_response)
            if req.method == 'PUT':
                env['wsgi.input'] = FileLikeIter(slow_iter(
                    req, env['wsgi.input'], data_to_read,
                    time_to_sleep))

        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    """
    paste.deploy app factory for creating WSGI proxy apps.
    """
    conf = global_conf.copy()
    conf.update(local_conf)

    def slow_filter(app):
        return SlowDown(app, conf)
    return slow_filter
