from functools import wraps

from flask import g, request

from .models import User


def token_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            return {
                "error": "Authentication required. Use a Bearer token."
            }, 401

        user = User.query.filter_by(api_token=token.strip()).first()
        if user is None:
            return {"error": "Invalid or expired authentication token."}, 401

        g.current_user = user
        return view(*args, **kwargs)

    return wrapped
