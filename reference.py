from flask import Flask, jsonify
import requests
from datetime import datetime, timezone

app = Flask(__name__)

def get_bus(stop, route):
    base_url = "https://api-v3.mbta.com"
    endpoint = "/predictions"
    params = {
        "filter[stop]": str(stop),
        "filter[route]": str(route),
        "api_key": "38b67b8f3fcf41bf91231644210ab865",
    }
    response = requests.get(base_url + endpoint, params=params)
    bus_data = []

    if response.status_code == 200:
        data = response.json()["data"]
        i = 0
        for prediction in data:
            arrival_time = prediction['attributes']['arrival_time']
            if arrival_time is not None:
                trip_id = prediction["relationships"]["trip"]["data"]["id"]
                #print("dp time: ", arrival_time)
                arrival_time = arrival_time[:-6]  # Remove the timezone offset
                print(arrival_time)
                arrival_datetime = datetime.strptime(arrival_time, '%Y-%m-%dT%H:%M:%S')
                current_datetime = datetime.now()
                print(current_datetime)
                minutes_until_arrival = (arrival_datetime - current_datetime).total_seconds() // 60

                print("Bus ", str(i), "will arrive in", minutes_until_arrival, "    TRIP ID:", trip_id)

                i += 1

                if int(minutes_until_arrival) < 0:
                    minutes_until_arrival = 0
               
                bus_data.append({"bus_" + str(i): str(int(minutes_until_arrival))})
                    
    else:
        bus_data.append({"Error": str(response.status_code)})

    return bus_data

@app.route('/')
def get_time():
    stop = 5034  # Replace with your desired stop ID
    #stop=5316 # test stop
    route = 101  # Replace with your desired route
    #return '[{"bus_1":"1"},{"bus_2":"2"},{"bus_3":"7"}]'
    try:
        bus_data = get_bus(stop, route)
    except Exception as e:
        return jsonify({"Error": str(e)})

    return jsonify(bus_data)

# USING gUNICORN TO RUN THIS SCRIPT

# app.run(host='0.0.0.0', port=5034)