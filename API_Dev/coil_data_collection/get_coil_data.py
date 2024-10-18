import time
from tqdm import tqdm
import requests
import json
import math
from datetime import datetime


# Target URL
url = 'http://10.96.182.179:5000/airconditioner'

fcu_speed_ovr_cmd = [3]
valve_ovr_cmd = [25, 30, 40, 50, 60, 70, 80, 90, 100]

total_time = 15 * 60

for fcu_speed in fcu_speed_ovr_cmd:
    for val in valve_ovr_cmd:
        control_action = {
            "room_temperature_setpoint": 23.0,
            "valve_ovr_flag": 1,
            "valve_ovr_cmd": val,
            "fcu_ss_ovr_flag": 0,
            "fcu_ss_ovr_cmd": 0,
            "fcu_speed_ovr_flag": 1,
            "fcu_speed_ovr_cmd": fcu_speed
        }
        json_data = json.dumps(control_action)

        while True:
            requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})
            for remaining in tqdm(range(10, 0, -1), desc="Countdown", unit="s"):
                time.sleep(1)
            response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})
            action_status = response.json()['data']
            if (int(action_status["valve_ovr_cmd"]) == int(val) and int(action_status["fcu_speed_ovr_cmd"]) ==
                    int(fcu_speed)):
                print(f"Control command has been executed successfully")
                break
            else:
                print(f"Control command failed. Retrying...")

        for remaining in tqdm(range(total_time, 0, -1), desc="Countdown", unit="s"):
            time.sleep(1)

        # Send GET request
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Get the returned JSON data
            data_file = response.json()
            data = data_file['data']
            # Save the data as a local JSON file
            now = datetime.now()
            file_name = ("ACUSupplyTemp_" + str(data["ACU_Supply_Temp"]) + "_FCUAirMassFlowRate_" +
                         str(data["FCU_air_mass_flowrate"]) + "_CHWSTemperature_" + str(data["chws_temperature"]) +
                         "_CHWFlowRateCalculated_" + str(data["chw_flow_rate_calculated"]) + "_" +
                         str(now.hour) + str(now.minute))

            with open(file_name + '.json', 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

            print("Data successfully saved...")
        else:
            print(f"Request failed, status code: {response.status_code}")
            data = None


