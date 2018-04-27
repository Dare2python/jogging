from flask import Blueprint
from ..auth import auth


api_auth = Blueprint('api_auth', __name__)


@api_auth.before_request
@auth.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


from . import users, routes
