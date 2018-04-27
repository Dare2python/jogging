from . import api
from .. import db
from ..models import Entry, Weather
from ..roles import Role
from flask import jsonify, request, g
import json
from sqlalchemy_filters import apply_filters, apply_pagination
# from flask_sqlalchemy import get_debug_queries


@api.route('/entries/', methods=['GET'])
def get_entries():
    """ Query Entries
    with Filtering capabilities
    e.g.:
    http://127.0.0.1:5000/api/v1/entries/?q={"filters":[{"field":"distance","op":"eq","value":"10"}]}
    http://127.0.0.1:5000/api/v1/entries/?q={"filters":[{"field":"date","op":"eq","value":"2018-04-14"}]}
    and Paging feature
    e.g.:
    http://127.0.0.1:5000/api/v1/entries/?q={"filters":[{"field":"date","op":"eq","value":"2018-04-15"},
    {"field":"distance","op":"eq","value":"7"}]}&page_number=1&page_size=1
    :return:
    JSON list of Entry instances
    """
    if g.user.role_id == Role.Admin:  # all records are allowed
        query = Entry.query

    elif g.user.role_id == Role.Manager:
        return jsonify({}), 403  # a user manager would be able to CRUD only users = no access to entries

    else:  # Regular user (or No role if data corrupted) - the most restrictive Regular
        query = Entry.query.filter(Entry.user_id == g.user.id)

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

    return jsonify({'entries': [entry.export_data() for entry in
                                query.all()]})


@api.route('/entries/<int:entry_id>', methods=['GET'])
def get_entry(entry_id):
    if g.user.role_id == Role.Admin:  # all records are allowed
        e = db.session.query(Entry).join(Weather).filter(Entry.id == entry_id).first()
        if e is None:
            return jsonify({}), 404
        w = db.session.query(Weather).join(Entry).filter(Entry.id == entry_id).first()
        return jsonify(e.export_data(), w.export_data())

    elif g.user.role_id == Role.Manager:
        return jsonify({}), 403  # a user manager would be able to CRUD only users = no access to entries

    else:  # Regular user (or No role if data corrupted) - the most restrictive Regular
        e = db.session.query(Entry).join(Weather).filter(Entry.id == entry_id). \
            filter(Entry.user_id == g.user.id).first()
        if e is None:
            return jsonify({}), 404
        w = db.session.query(Weather).join(Entry).filter(Entry.id == entry_id).first()
        return jsonify(e.export_data(), w.export_data())


@api.route('/entries/', methods=['POST'])
def new_entry():
    if g.user.role_id == Role.Manager:
        return jsonify({}), 403  # a user manager would be able to CRUD only users = no access to entries

    entry = Entry()
    entry.import_data(request.json, g.user.id if g.user else 1)
    db.session.add(entry)
    db.session.commit()
    weather = Weather()
    weather.get_weather(entry.id, entry.latitude, entry.longitude, entry.date)
    db.session.add(weather)
    db.session.commit()
    return jsonify({}), 201, {'Location': entry.get_url()}


@api.route('/entries/<int:entry_id>', methods=['PUT'])
def edit_entry(entry_id):
    if g.user.role_id == Role.Admin:  # all records are allowed
        entry = Entry.query.get_or_404(entry_id)
        entry.import_data(request.json, g.user.id if g.user else 1)
        db.session.add(entry)
        db.session.commit()
        return jsonify({})

    elif g.user.role_id == Role.Manager:
        return jsonify({}), 403  # a user manager would be able to CRUD only users = no access to entries

    else:  # Regular user (or No role if data corrupted) - the most restrictive Regular
        entry = db.session.query(Entry).filter(Entry.id == entry_id).\
            filter(Entry.user_id == g.user.id).first()
        if entry is None:
            return jsonify({}), 404
        entry.import_data(request.json, g.user.id if g.user else 1)
        db.session.add(entry)
        db.session.commit()
        return jsonify({})


@api.route('/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    if g.user.role_id == Role.Admin:  # all records are allowed
        entry = Entry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        return jsonify({})

    elif g.user.role_id == Role.Manager:
        return jsonify({}), 403  # a user manager would be able to CRUD only users = no access to entries

    else:  # Regular user (or No role if data corrupted) - the most restrictive Regular
        entry = db.session.query(Entry).filter(Entry.id == entry_id).\
            filter(Entry.user_id == g.user.id).first()
        if entry is None:
            return jsonify({}), 404
        entry.import_data(request.json, g.user.id if g.user else 1)
        db.session.delete(entry)
        db.session.commit()
        return jsonify({})


