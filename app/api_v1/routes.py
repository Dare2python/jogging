from . import api
from flask import jsonify, url_for


@api.route('/')
def describe():
    return jsonify({'entries': url_for('api.get_entries',  _external=True),
                    'reports': url_for('api.get_report', week_start='2018-04-12', _external=True)
                    })

