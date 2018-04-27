from flask import Blueprint
from ..auth import auth_token, auth


api = Blueprint('api', __name__)


@api.before_request
# @auth_token.login_required
@auth.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


from . import routes, entries, reports
