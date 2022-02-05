from requests import get
from twilio.rest import Client
import os

APPID = os.environ.get("APPID")
LAT = os.environ.get("LAT")
LAT2 = os.environ.get("LAT2")
LON2 = os.environ.get("LON2")
LONG = os.environ.get("LONG")
OWM_ENDPOINT = "https://api.openweathermap.org/data/2.5/onecall"

# TWILIO
SID = os.environ.get("TWILIO_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH")
print(os.environ.get("TWILIO_SID"))
params = {
    "appid": APPID,
    "lat": LAT,
    "lon": LONG,
    "exclude": "current,minutely,daily"
}
will_rain = False

with get(OWM_ENDPOINT, params=params) as data:
    data.raise_for_status()
    weather_data = data.json()
    for i in range(12):
        if int(weather_data["hourly"][i]["weather"][0]["id"]) < 600:
            will_rain = True
if will_rain:
    client = Client(SID, AUTH_TOKEN)
   #phone numbers removed for privacy
    message = client.messages \
        .create(
        body="It's going to rain today. Remember to bring an ☔️",
        from_='fromphone',
        to='tophone')
    print(message.status)
