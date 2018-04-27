#! /usr/bin/python

import os
from app import create_app, db
from app.models import User, Entry, Weather
from app.roles import Role
import datetime


if __name__ == '__main__' or __name__ == 'run':
    app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
    with app.app_context():
        db.create_all()
        # create a development user and 2 sample entries
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

    app.run()
