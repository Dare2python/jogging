from . import api
from ..models import Report
from flask import jsonify


@api.route('/reports/<week_start>', methods=['GET'])
def get_report(week_start):
    r = Report(week_start)
    return jsonify(r.export_data())
