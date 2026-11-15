"""Tiny router: @route(method, pattern, roles) registers an API function. Made by Krisanu.
roles=None means public, "any" means any logged-in user, or a list such as ["hospital"]."""
import re

ROUTES = []


class ApiError(Exception):
    def __init__(self, message, code=400):
        super().__init__(message)
        self.code = code


class Ctx:
    """What a route function receives: the user, the JSON body, the query string, the URL parts and the visitor's IP."""
    def __init__(self, user, body, query, args, ip="-"):
        self.user, self.body, self.query, self.args, self.ip = user, body, query, args, ip
        self.set_cookie = None
        self.clear_cookie = False

    def need(self, *names):
        missing = [n for n in names if self.body.get(n) in (None, "")]
        if missing:
            raise ApiError("Please fill in: " + ", ".join(missing))
        return [self.body[n] for n in names]

    def q(self, name, default=""):
        return (self.query.get(name) or [default])[0]


def route(method, pattern, roles=None):
    regex = re.compile("^" + re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", pattern) + "$")

    def register(function):
        ROUTES.append((method, regex, roles, function))
        return function
    return register


def dispatch(method, path, query, body, user, ip="-"):
    for route_method, regex, roles, function in ROUTES:
        match = regex.match(path)
        if route_method != method or not match:
            continue
        if roles is not None:
            if not user:
                raise ApiError("Please log in first.", 401)
            if roles != "any" and user["role"] not in roles:
                raise ApiError("You do not have access to this.", 403)
        ctx = Ctx(user, body, query, match.groupdict(), ip)
        return function(ctx), ctx
    raise ApiError("Not found", 404)
