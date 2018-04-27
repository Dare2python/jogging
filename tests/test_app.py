import unittest
from app import create_app, db
from app.models import User, Entry, Weather
from app.roles import Role
import datetime
import base64


class EntryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        db.create_all()
        self.client = self.app.test_client()
        if User.query.get(1) is None:
            admin = User("admin", Role.Admin)
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()

            manager = User("manager", Role.Manager)
            manager.set_password("manager")
            db.session.add(manager)
            db.session.commit()

            entry = Entry(date=datetime.date(2018, 4, 13), distance=10,
                          time=datetime.time(hour=1, minute=1, second=30),
                          latitude=50.11, longitude=36.11, user_id=admin.id)
            db.session.add(entry)
            db.session.commit()

            weather = Weather()
            weather.get_weather(entry.id, entry.latitude, entry.longitude, entry.date)
            db.session.add(weather)
            db.session.commit()

            entry = Entry(date=datetime.date(2018, 4, 14), distance=0.2,
                          time=datetime.time(minute=5, second=30),
                          latitude=50.22, longitude=35.22, user_id=admin.id)
            db.session.add(entry)
            db.session.commit()

            weather = Weather()
            weather.get_weather(entry.id, entry.latitude, entry.longitude, entry.date)
            db.session.add(weather)
            db.session.commit()

    def tearDown(self):
        self.app_ctx.pop()

    def test_auth(self):
        r = self.client.get('/api/v1/entries/?q={"filters":[{"field":"distance","op":"eq","value":"10"}]}')
        self.assertEqual(r.status_code, 401)  # No authentication
        # print(r.get_data(as_text=True))
        self.assertTrue('unauthorized' in r.get_data(as_text=True))

    def test_filter(self):
        username = 'admin'
        password = 'admin'
        method = 'GET'
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(bytes(username + ":" + password, 'ascii')).decode('ascii')
        }
        r = self.client.open('/api/v1/entries/?q={"filters":[{"field":"distance","op":"eq","value":"10"}]}',
                             method=method, headers=headers)
        self.assertEqual(r.status_code, 200)  # No authentication
        # print(r.get_data(as_text=True))
        self.assertTrue('"distance": 10.0' in r.get_data(as_text=True))

    def test_paging(self):
        username = 'admin'
        password = 'admin'
        method = 'GET'
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(bytes(username + ":" + password, 'ascii')).decode('ascii')
        }
        r = self.client.open('/api/v1/entries/?page_number=1&page_size=1',
                             method=method, headers=headers)
        self.assertEqual(r.status_code, 200)  # No authentication
        # print(r.get_data(as_text=True))
        self.assertTrue('"distance": 10.0' in r.get_data(as_text=True))


