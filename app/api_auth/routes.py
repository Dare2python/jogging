from . import api_auth
from ..auth import auth
from flask import jsonify, url_for, g


@api_auth.route('/get-auth-token')
@auth.login_required
def get_auth_token():
    return jsonify({'token': g.user.generate_auth_token()})


@api_auth.route('/')
@auth.login_required
def describe():
    return jsonify({'users': url_for('api_auth.get_users',  _external=True),
                    'token': url_for('api_auth.get_auth_token',  _external=True)
                    })
