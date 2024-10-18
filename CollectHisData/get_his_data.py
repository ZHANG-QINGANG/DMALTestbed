import time
from tqdm import tqdm
import requests
import json
import pandas as pd
import os


# Target URL
url = 'http://10.96.182.179:5000/airconditioner'

fcu_speed_ovr_cmd = [1]
valve_ovr_cmd = [45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

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
            if int(action_status["fcu_speed_ovr_cmd"]) == int(fcu_speed) and action_status["valve_ovr_cmd"] == int(val):
                print(f"Control command has been executed successfully")
                break
            else:
                print(f"Control command failed. Retrying...")

        for remaining in tqdm(range(30 * 60, 0, -1), desc="Waite for steady state...", unit="s"):
            time.sleep(1)

        for remaining in tqdm(range(60, 0, -1), desc="Collect data...", unit="s"):
            # Send GET request
            response = requests.get(url)
            # Check if the request was successful
            if response.status_code == 200:
                # Get the returned JSON data
                data_file = response.json()
                data = data_file['data']
                df = pd.DataFrame([data])
                df.set_index("time", inplace=True)
                file_path = f"./HisData/experiment_data_valve.csv"
                if not os.path.isfile(file_path):
                    df.to_csv(file_path)
                else:
                    df.to_csv(file_path, mode='a', header=False)
                print("Data successfully saved...")
            else:
                print(f"Request failed, status code: {response.status_code}")
                data = None

            time.sleep(30)


