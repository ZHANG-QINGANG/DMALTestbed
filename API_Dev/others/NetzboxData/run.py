import requests
import json
import urllib3

# Disable SSL warnings (for self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Base URL of your server
base_url = "https://0.0.0.0:8090"

# Login URL
login_url = f"{base_url}/rest/session"

# API URL to fetch data after login
api_url = f"{base_url}/rest/assets"

# JSON payload for login
with open('login_data.json', 'r') as file:
    login_data = json.load(file)

# Only include essential headers
headers = {
    "Content-Type": "application/json",  # Informing the server we're sending JSON data
    "Accept": "application/json"  # Expecting a JSON response
}


def digest_data(data):
    sensor_types = ["RELATIVE_HUMIDITY", "TEMPERATURE"]
    sensor_names = ["R1_Front_Top", "R1_Front_Middle", "R1_Front_Bottom",
                    "R1_Back_Top", "R1_Back_Middle", "R1_Back_Bottom",
                    "R2_Front_Top", "R2_Front_Middle", "R2_Front_Bottom",
                    "R2_Back_Top", "R2_Back_Middle", "R2_Back_Bottom",
                    "ACU_Supply", "ACU_Return"]

    sensor_data = {}

    # Loop through the items and extract the required information
    for item in data['items']:
        label = item.get("label", "")
        sensor_type = item.get("sensorType", "")

        # Check if the label matches one of the sensor names and if the sensorType matches
        matching_sensor = next((name for name in sensor_names if name in label), None)

        if matching_sensor and sensor_type in sensor_types:
            # Generate the key as "sensor name + sensor type"
            key = f"{matching_sensor} {sensor_type}"

            # Get the current sensor value
            value = item["currentSensorValue"]["value"]

            # Store the value in the dictionary
            sensor_data[key] = value

    return sensor_data


# Start a session to persist cookies across requests
with requests.Session() as session:
    # Send POST request to login
    from requests.auth import HTTPBasicAuth

    response = session.post(login_url, headers=headers, auth=HTTPBasicAuth('superuser', 'dmaltestbed'), verify=False)

    # Check if login was successful
    if response.status_code == 200:
        print("Login successful!")

        # You can print the cookies or tokens after login
        print("Cookies after login:", session.cookies.get_dict())

        # Now send a GET request to the API to fetch the JSON data
        api_response = session.get(api_url, headers=headers, verify=False)

        if api_response.status_code == 200:
            # Parse and print the JSON data from the API
            json_data = api_response.json()
            thermal_data = digest_data(json_data)
            print(f"thermal data: {thermal_data}")
            with open('api_data.json', 'w') as outfile:
                json.dump(thermal_data, outfile, indent=4)
        else:
            print(f"Failed to retrieve data, status code: {api_response.status_code}")
            print(f"Response content: {api_response.text}")
    else:
        print(f"Login failed, status code: {response.status_code}")
        print(f"Response content: {response.text}")
