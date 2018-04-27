import requests
import json
import geocoder
from datetime import datetime


def request_weather(latitude, longitude, date):
    # uri = "http://history.openweathermap.org/data/2.5/history/city?" \
    #       "lat={lat}&lon={lon}&type=hour&start={start}&cnt={cnt}&APPID={APIKEY}"
    # true history data requires payed access
    uri = "http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&APPID={APIKEY}"
    api_key = "7e773aa2a8eedfd64528ad9bf3572aae"

    url = uri.format(lat=latitude, lon=longitude, start=date, cnt=1, APIKEY=api_key)
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)
    main, temp, pressure, humidity = None, None, None, None

    if response.ok:
        j_data = response.json()
        main = j_data['weather'][0]['main']
        temp = j_data['main']['temp']
        pressure = j_data['main']['pressure']
        humidity = j_data['main']['humidity']
    else:
        response.raise_for_status()
    return main, temp, pressure, humidity


if __name__ == '__main__':
    print(request_weather(geocoder.ip('me').lat, geocoder.ip('me').lng, datetime.now().date().isoformat()))
