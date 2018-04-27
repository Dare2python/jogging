from app import db
import datetime
from dateutil import parser as datetime_parser
# from dateutil.tz import tzutc
import geocoder
from app.exceptions import ValidationError, WeatherError
from app.weather import request_weather
from flask import url_for, current_app
from sqlalchemy.sql import text
# from flask_sqlalchemy import get_debug_queries
from collections import namedtuple
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .roles import Role


class Entry(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    distance = db.Column(db.Float, default=0)
    time = db.Column(db.Time)
    latitude = db.Column(db.Float, default=geocoder.ip('me').lat)
    longitude = db.Column(db.Float, default=geocoder.ip('me').lng)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        index=True)
    weather = db.relationship('Weather')

    def __init__(self, date=None, distance=0, time=None, latitude=0, longitude=0, user_id=1):
        self.date = date
        self.distance = distance
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.user_id = user_id

    def get_url(self):
        return url_for('api.get_entry', entry_id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'id': str(self.id),
            'date': str(self.date),
            'distance': self.distance,
            'time': str(self.time),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'user_id': self.user_id
        }

    def import_data(self, data, user_id):
        try:
            self.user_id = user_id
            self.date = datetime_parser.parse(data['date']).date()
            self.distance = data['distance']
            self.time = datetime_parser.parse(data['time']).time()
            self.latitude = data['latitude']
            self.longitude = data['longitude']
        except KeyError as e:
            raise ValidationError('Invalid Entry: missing ' + e.args[0])
        return self

    def __repr__(self):
        return "<Entry(id='%s', date='%s', distance='%s', time='%s', latitude='%s', longitude='%s')>" % (
                                self.id, self.date, self.distance, self.time, self.latitude, self.longitude)


class Weather(db.Model):
    __tablename__ = 'weather'
    id = db.Column(db.Integer, primary_key=True)
    main = db.Column(db.String(32), index=True)
    temp = db.Column(db.Integer, index=True)
    pressure = db.Column(db.Integer, index=True)
    humidity = db.Column(db.Integer, index=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'),
                         index=True)

    def get_weather(self, entry_id, latitude, longitude, date):
        self.entry_id = entry_id
        try:
            self.main, self.temp, self.pressure, self.humidity = \
                request_weather(latitude, longitude, date)
        except Exception as e:
            raise WeatherError('Weather error:' + e.args[0])
        return self

    def export_data(self):
        return {
            'id': str(self.id),
            'main': self.main,
            'temp': self.temp,
            'pressure': self.pressure,
            'humidity': self.humidity,
            'entry_id': self.entry_id
        }

    def __repr__(self):
        return "<Weather(id='%s', main='%s', temp='%s', pressure='%s', humidity='%s', entry_id='%s')>" % (
                                self.id, self.main, self.temp, self.pressure, self.humidity, self.entry_id)


class Report:
    """Calculates average speed & distance per week"""

    def __init__(self, week_start):
        self.start = datetime_parser.parse(week_start).date()
        self.speed = 0
        self.distance = 0
        s = text("SELECT AVG(entries.distance/(strftime('%H', entries.time)"
                 "+ strftime('%M', entries.time)/60.0 "
                 "+ strftime('%S', entries.time)/3600.0))  AS average, "
                 "SUM(entries.distance) AS distance FROM entries "
                 "WHERE entries.date BETWEEN :start and :finish")
        result = db.engine.execute(s,
                                   {'start': self.start.isoformat(),
                                    'finish': (self.start +
                                               datetime.timedelta(days=7)
                                               ).isoformat()})
        Record = namedtuple('Record', result.keys())
        records = [Record(*r) for r in result.fetchall()]
        self.speed = records[0].average
        self.distance = records[0].distance
        # print(get_debug_queries()[0])

    def export_data(self):
        return {
            'speed': self.speed,
            'distance': self.distance
        }

    def __repr__(self):
        return "<Report(start='%s', speed='%s', distance='%s')>" % (
                                self.start, self.speed, self.distance)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer)

    def __init__(self, username="", role_id=Role.Regular):
        self.username = username
        self.role_id = role_id

    def get_url(self):
        return url_for('api_auth.get_user', user_id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'id': str(self.id),
            'username': self.username,
            'role_id': self.role_id
            #  'password_hash': self.password_hash  # debug only!
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    def import_data(self, data, role_id=Role.Regular):
        try:
            self.username = data['username']
            self.set_password(data['password'])
            self.role_id = role_id
        except KeyError as e:
            raise ValidationError('Invalid User: missing ' + e.args[0])
        return self

    def set_role(self, role_id):
        self.role_id = role_id

    def is_manager(self):
        return self.role_id == Role.Manager

    def is_admin(self):
        return self.role_id == Role.Admin

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None  # the token is invalid
        return User.query.get(data['id'])  # valid token contains User ID for the token

    def __repr__(self):
        return "<User(id='%s', username='%s', password_hash='%s')>" % (
                                self.id, self.username, self.password_hash)
