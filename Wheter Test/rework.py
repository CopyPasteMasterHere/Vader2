from datetime import datetime, timedelta
import requests
from pysondb import db
from flask import Flask, render_template, request
import schedule
from threading import Thread, Event

global_decision = 10
global_forcast = []

first_run = True
curr_sched = False

class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(1):
            schedule.run_pending()
            print("hello")

def get_sunset_and_sunrise():
    try:
        response = requests.get("https://api.sunrise-sunset.org/json?lat=58.557609&lon=15.0077623&date=today")
        json_object = response.json()
        js2 = json_object["results"]
        sunset = js2["sunset"]
        sunrise = js2["sunrise"]

        
        in_time = datetime.strptime(sunset, "%I:%M:%S %p")
        out_time = datetime.strftime(in_time, "%H:%M:%S")
        sunset = out_time

        in_time2 = datetime.strptime(sunrise, "%I:%M:%S %p")
        out_time2 = datetime.strftime(in_time2, "%H:%M:%S")
        sunrise = out_time2
        return sunset, sunrise
    except:
        return "Error"

def hour_rounder(t):
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour) 
    +timedelta(hours=t.minute//30))

def get_forecast():
    forecast = []
    try:
        user_agent = {'User-agent': 'calle'}
        response = requests.get("https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=58.557609&lon=15.0077623&altitude=67", headers=user_agent)
        j_respons = response.json() 
        return j_respons
    except:
        return "Error"

def get_relevant_forcast(hours_after_sunrise):

    sunset, sunrise = get_sunset_and_sunrise()
    r_sunset = hour_rounder(datetime.strptime(f'{sunset}',"%H:%M:%S")).hour 
    r_sunrise = hour_rounder(datetime.strptime(f'{sunrise}',"%H:%M:%S")).hour

    j_forcast = get_forecast()
    parsed_forcast = []
    relevant_forcast = []

    for i in range(len(j_forcast["properties"]["timeseries"])):
        parsed_forcast.append(j_forcast["properties"]["timeseries"][i])

    parsed_forcast = parsed_forcast[0:20]

    for j in parsed_forcast:

        time = j["time"]
        time = datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ")


        
        if r_sunrise <= time.hour <= int(r_sunrise) + int(hours_after_sunrise):
            relevant_forcast.append(j["data"]["next_1_hours"]["summary"]["symbol_code"])

    return relevant_forcast

def get_data_from_db(name):
    j_db=db.getDb("database.json")
    q = {"test": "1"}
    data = j_db.getByQuery(query=q)
    data = str(data).split(",")
    for i in data:
        if name in i:
            i = str(i).split(":")
            data = i[1].replace("}", "")
            data = data.replace("]", "")
            data = data.replace("'", "")
            data = data.replace(" ", "")
            return data

def store_data_in_db(path, new_value):
    j_db=db.getDb("database.json")
    query_data = {path: get_data_from_db(path)}
    updated_data = {path: new_value}
    print(query_data, updated_data)
    j_db.updateByQuery(db_dataset=query_data, new_dataset=updated_data)

def get_weather_score(forcast):
    score = 0
    for i in forcast:
        if "partlycloudy" in i:
            score += int(get_data_from_db("partlycloudy"))
        elif "cloudy" in i:
            score += int(get_data_from_db("fair"))
        elif "fair" in i:
            score += int(get_data_from_db("cloudy"))
        elif "thunder" in i:
            score += int(get_data_from_db("thunder"))
        elif "clearsky" in i:
            score += int(get_data_from_db("clearsky"))
    return int(score)/len(forcast)

def relay_decision(decision):
    print(decision, get_data_from_db("decision_num"))
    url_off = "http://192.168.68.81/netio.cgi?pass=netio&output1=0"
    url_on = "http://192.168.68.81/netio.cgi?pass=netio&output1=1"
    try:
        if decision > float(get_data_from_db("decision_num")):
            print("hiufdsahgfiasdgfgiydsyigfgysdyigfdsgyuygufdsgyufgyuesuyfgds")
            requests.get(url_on)
            
        else:
            print("off")
            requests.get(url_off)
    except:
        print("error")

def control():
    relevant_forcast = get_relevant_forcast(get_data_from_db("hours_after_sunrise"))
    weather_score = get_weather_score(relevant_forcast)
    return weather_score, relevant_forcast
    
def new_control():
    global first_run
    global curr_sched
    if first_run == True:
        update_forcast_and_decision()
        first_run = False
    elif curr_sched == False:
        print("started sched")
        schedule.every().day.at("02:00:00").do(update_forcast_and_decision)
        curr_sched = True
    else:
        print("curr shed True, not sched more")      

def update_forcast_and_decision():
    print("fdyisfysdgfsdyfgsdyifgsdyfgydsyfds")
    global curr_sched
    global first_run
    global global_decision
    global global_forcast
    relevant_forcast = get_relevant_forcast(get_data_from_db("hours_after_sunrise"))
    weather_score = get_weather_score(relevant_forcast)
    global_decision = weather_score
    global_forcast = relevant_forcast
    if first_run == False:
        curr_sched = False

my_event = Event()
thread = MyThread(my_event)
thread.start()

app = Flask(__name__)

@app.route('/', methods =["GET", "POST"])
def website():
    global global_decision
    global global_forcast
    
    #schedule.every().day.at("13:26").do(called_at_time)
    #weather_score, relevant_forcast = new_control()
    #relay_decision(weather_score)
    new_control()

    if request.method == "POST":
        name = request.form.get("subName")
        value = request.form.get("subValue")
        if name and value:
            try:
                store_data_in_db(name, value)
            except:
                pass
    return render_template('index.html', partlycloudy = get_data_from_db("partlycloudy"), cloudy = get_data_from_db("cloudy"), fair = get_data_from_db("fair"), thunder = get_data_from_db("thunder"), clearsky = get_data_from_db("clearsky"), hours_after_sunrise = get_data_from_db("hours_after_sunrise"), relevant_forcast = global_forcast, weather_score = global_decision)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
    
