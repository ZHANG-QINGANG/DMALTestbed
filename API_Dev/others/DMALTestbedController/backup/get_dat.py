import requests
import json

# Target URL
url = 'http://10.96.182.179:5001/airconditioner'

# Send GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Get the returned JSON data
    data = response.json()

    # Save the data as a local JSON file
    with open('airconditioner_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print("Data successfully saved to airconditioner_data.json file")
else:
    print(f"Request failed, status code: {response.status_code}")
