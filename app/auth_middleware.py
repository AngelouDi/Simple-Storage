from flask import session, redirect, url_for
from functools import wraps


def is_user(f):
    @wraps(f)
    # TODO: add authentication everytime that user exists in db
    def decorated(*args, **kwargs):
        username = None
        try:
            username = session["username"]
        except KeyError as e:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


