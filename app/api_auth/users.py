from . import api_auth
from app import db
from app.models import User
from app.roles import Role
from flask import jsonify, request, g
import json
from sqlalchemy_filters import apply_filters, apply_pagination
# from flask_sqlalchemy import get_debug_queries


@api_auth.route('/users/', methods=['GET'])
def get_users():
    """ Query users
    with Filtering and Paging capabilities
    e.g.:
    http://127.0.0.1:5000/auth/users/?q={"filters":[{"field":"role_id","op":"eq","value":"3"}]}
    &page_number=1&page_size=1
    :return:
    JSON list of User instances
    """
    if g.user.role_id == Role.Admin or g.user.role_id == Role.Manager:
        query = User.query
        if request.query_string:
            q_param = request.args.get('q')
            if q_param:
                q = json.loads(q_param)
                for f in q['filters']:
                    query = apply_filters(query, f)

            page_number = request.args.get('page_number')
            page_size = int(request.args.get('page_size', default=10))
            if page_number:
                page_number = int(page_number)
                query, pagination = apply_pagination(query, page_number=page_number, page_size=page_size)
        return jsonify({'users': [user.export_data() for user in
                                  query.all()]})
    else:
        return jsonify({}), 403


@api_auth.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if g.user.role_id == Role.Admin or g.user.role_id == Role.Manager:
        user = User.query.get_or_404(user_id)
        return jsonify(user.export_data())
    else:
        return jsonify({}), 403


@api_auth.route('/users/', methods=['POST'])
def new_user():
    if g.user.role_id == Role.Admin or g.user.role_id == Role.Manager:
        user = User()
        user.import_data(request.json, Role.Regular)
        db.session.add(user)
        db.session.commit()
        return jsonify({}), 201, {'Location': user.get_url()}
    else:
        return jsonify({}), 403


@api_auth.route('/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    if g.user.role_id == Role.Admin or g.user.role_id == Role.Manager:
        user = User.query.get_or_404(user_id)
        user.import_data(request.json)
        db.session.add(user)
        db.session.commit()
        return jsonify({})
    else:
        return jsonify({}), 403


@api_auth.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if g.user.role_id == Role.Admin or g.user.role_id == Role.Manager:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({})
    else:
        return jsonify({}), 403
