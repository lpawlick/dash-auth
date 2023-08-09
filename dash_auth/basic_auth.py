import base64
from typing import Optional, Union, Callable
import flask
from dash import Dash

from .auth import Auth


class BasicAuth(Auth):
    def __init__(
        self,
        app: Dash,
        username_password_list: Union[list, dict, Callable[[str, str], str]],
        public_routes: Optional[list] = None,
    ):
        """Add basic authentication to Dash.

        :param app: Dash app
        :param username_password_list: username:password list, either as a
            list of tuples or a dict or a callable function that returns a string
        :param public_routes: list of public routes, routes should follow the
            Flask route syntax
        """
        Auth.__init__(self, app, public_routes=public_routes)
        if isinstance(username_password_list, dict):
            self._auth = username_password_list
        elif isinstance(username_password_list, list):
            self._auth = {k: v for k, v in username_password_list}
        elif callable(username_password_list):
            self._auth = username_password_list
        else:
            raise ValueError("username_password_list must be a list, dict, or callable")

    def is_authorized(self):
        header = flask.request.headers.get('Authorization', None)
        if not header:
            return False
        username_password = base64.b64decode(header.split('Basic ')[1])
        username_password_utf8 = username_password.decode('utf-8')
        username, password = username_password_utf8.split(':', 1)
        if callable(self._auth):
            return self._auth(username, password)
        else:
            return self._auth.get(username) == password

    def login_request(self):
        return flask.Response(
            'Login Required',
            headers={'WWW-Authenticate': 'Basic realm="User Visible Realm"'},
            status=401
        )

    def auth_wrapper(self, f):
        def wrap(*args, **kwargs):
            if not self.is_authorized():
                return flask.Response(status=403)

            response = f(*args, **kwargs)
            return response
        return wrap

    def index_auth_wrapper(self, original_index):
        def wrap(*args, **kwargs):
            if self.is_authorized():
                return original_index(*args, **kwargs)
            else:
                return self.login_request()
        return wrap
