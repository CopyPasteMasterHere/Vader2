from decimal import Rounded
import requests
from datetime import datetime, timedelta

forecast = []
power_pin = False

#need to add offset and find out if offset is +2 in summer?
def get_sunset_and_sunrise():
    response = requests.get("https://api.met.no/weatherapi/sunrise/2.0/.json?lat=58.557609&lon=15.0077623&date=2022-05-15&offset=+01:00")
    split_data = str(response.text).split("}")
    for i in split_data:
        if "LOCAL DIURNAL SUN RISE" in i:
            sunrise = ""
            sunrise = i[63:71]
        if "LOCAL DIURNAL SUN SET" in i:
            sunset = ""
            sunset = i[61:69]
    return sunset, sunrise

def get_forecast(forecast):
    user_agent = {'User-agent': 'calle'}
    response2 = requests.get("https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=58.557609&lon=15.0077623&altitude=67", headers=user_agent)
    split_data2 = str(response2.text).split("}")
    for i in split_data2: 
        if "symbol_code" in i and "next_1_hours" in i:
            forecast.append(i[42:])
    return forecast

def hour_rounder(t):
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

def control():

    a = get_sunset_and_sunrise()
    f = get_forecast(forecast)

    time_1 = datetime.strptime(f'{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}',"%H:%M:%S")
    time_2 = datetime.strptime(f'{a[0]}',"%H:%M:%S")
    time_interval = time_2 - time_1 

    rounded_time_to_sunset_obj = hour_rounder(datetime.strptime(f'{time_interval}',"%H:%M:%S"))
    time_to_sunset = int(rounded_time_to_sunset_obj.hour)
    relevant_symbols = []
    for i in range(time_to_sunset):
        relevant_symbols.append(f[i])
    print(relevant_symbols)

control()