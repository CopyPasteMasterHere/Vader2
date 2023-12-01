import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request


def get_sym_dict():

    with open('sym.txt', "r") as sym:
        c = sym.read()
        a = c.split(",")
        sym.close()


    sym_dict = {
        "cloudy" : a[0],
        "partlycloudy" : a[1],
        "fair" : a[2],
        "rain" : a[3],
        "thunder" : a[4],
        "clearsky" : a[5]
    }

    return sym_dict


#need to add offset and find out if offset is +2 in summer?
#def get_sunset_and_sunrise(Sommartid):
#    response = requests.get(f"https://api.met.no/weatherapi/sunrise/2.0/.json?lat=58.557609&lon=15.0077623&altitude=67")
#    split_data = str(response.text).split("}")
#    print(split_data)
#    print("hello")
#    for i in split_data:
#        if "LOCAL DIURNAL SUN RISE" in i:
#            sunrise = ""
#            sunrise = i[63:71]
#        if "LOCAL DIURNAL SUN SET" in i:
#            sunset = ""
#            sunset = i[61:69]
#    return sunset, sunrise
def get_sunset_and_sunrise():
    response = requests.get("https://api.sunrise-sunset.org/json?lat=58.557609&lon=15.0077623&date=today")
    json_object = response.json()
    js2 = json_object["results"]
    sunset = js2["sunset"]
    sunrise = js2["sunrise"]

    from datetime import datetime
    in_time = datetime.strptime(sunset, "%I:%M:%S %p")
    out_time = datetime.strftime(in_time, "%H:%M:%S")
    sunset = out_time

    in_time2 = datetime.strptime(sunrise, "%I:%M:%S %p")
    out_time2 = datetime.strftime(in_time2, "%H:%M:%S")
    sunrise = out_time2
    return sunset, sunrise

def get_forecast():
    forecast = []
    user_agent = {'User-agent': 'calle'}
    response2 = requests.get("https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=58.557609&lon=15.0077623&altitude=67", headers=user_agent)
    split_data2 = str(response2.text).split("}")
    for i in split_data2: 
        if "symbol_code" in i and "next_1_hours" in i:
            forecast.append(i[42:])
    return forecast

def get_decision(rel_f, dict_symbol):

    decision = 0

    for i in rel_f:
        print(i)
        if "partlycloudy_night" in i or "partlycloudy" in i:
            decision += float(dict_symbol.get("partlycloudy"))
            print(f"1 {decision}")
        elif "cloudy" in i or "cloudy_night" in i:
            decision += float(dict_symbol.get("cloudy"))
            print(f"2 {decision}")
        elif "fair" in i or "fair_night" in i:
            decision += float(dict_symbol.get("fair"))
            print(f"3 {decision}")
        elif "rain" in i or "rain_night" in i:
            decision += float(dict_symbol.get("rain"))
            print(f"4 {decision}")
        elif "thunder" in i or "thunder_night" in i:
            decision += float(dict_symbol.get("thunder"))
            print(f"5 {decision}")
        elif "clearsky" in i or "clearsky_night" in i:
            decision += float(dict_symbol.get("clearsky"))
            print(f"6 {decision}")
        else:
            print("somethings wrong")
    print(f"decision is {decision}")

    return decision

def hour_rounder(t):
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour) 
    +timedelta(hours=t.minute//30))

def control():
    sym_dict = get_sym_dict()
    a = get_sunset_and_sunrise()
    f = get_forecast()
    sunset = a[0]
    sunrise = a[1]

    time_1 = datetime.strptime(f'{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}',"%H:%M:%S")
    #time_1 = datetime.strptime(f"01:00:00", "%H:%M:%S")
    time_2 = datetime.strptime(f'{sunrise}',"%H:%M:%S")
    time_interval = time_2 - time_1
    
    print(time_1, time_2)
    print(time_interval)

    try:
        rounded_time_to_sunrise_obj = hour_rounder(datetime.strptime(f'{time_interval}',"%H:%M:%S"))
    except:
        rounded_time_to_sunrise_obj = hour_rounder(datetime.strptime(f'{time_interval}',"-1 day, %H:%M:%S"))

    time_to_sunrise = int(rounded_time_to_sunrise_obj.hour) #Time to sunrise
    time_to_sunrise = time_to_sunrise

    print(time_to_sunrise)

    f1 = f[time_to_sunrise:]
    f2 = f1[:5] #f2 is the fist 5 hours after sunrise

    decision = get_decision(f2, sym_dict)

    return decision, f2, sunset, sunrise, sym_dict

app = Flask(__name__)

@app.route('/', methods =["GET", "POST"])
def hello():

    info = control()
    score = info[0]
    weather = info[1]
    sunset = info[2]
    sunrise = info[3]
    sym_dict = info[4]

    if request.method == "POST":
        name = request.form.get("subName")
        value = request.form.get("subValue")
        if name and value:
            with open('sym.txt', "r") as sym:
                new_value = dict(zip(sym_dict, range(1, len(sym_dict)+1)))
                c = sym.read()
                b = c.split(",")
                b[int(new_value.get(f"{name}")) - 1] = value
                print(value)

                txt = ""
                for i in b:
                    txt = txt + str(i) + ","
                txt = txt[:-1]

            sym.close()

            f = open("sym.txt", "w")
            f.write(txt)
            f.close()

    
    return render_template('html.html', score=score, weather=weather, sunset=sunset, sunrise=sunrise, sym_dict=sym_dict)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=False)
    


#Todo
# get sunset and sunrise data at correct time
# Fix html