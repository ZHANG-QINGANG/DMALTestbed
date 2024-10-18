import requests
import json
import math
import time
# Target URL
url = 'http://10.96.182.179:5000/airconditioner'

# Send GET request
response = requests.get(url)

i = 0
while True:
    # Check if the request was successful
    if response.status_code == 200:
        # Get the returned JSON data
        data_file = response.json()
        data = data_file['data']
        # Save the data as a local JSON file
        # with open('airconditioner_data.json', 'w', encoding='utf-8') as json_file:
        #     json.dump(data, json_file, ensure_ascii=False, indent=4)
        #
        # print("Data successfully saved to airconditioner_data.json file")
        with open(str(i) + '.json', 'w') as json_file:
            json.dump(data, json_file)
        i += 1
        print('waiting...')
        time.sleep(15)
    else:
        print(f"Request failed, status code: {response.status_code}")
        data = None







# def saturation_vapor_pressure(T):
#     return 0.6108 * math.exp((17.27 * T) / (T + 237.3))  # 单位：kPa
#
#
# def air_enthalpy(T_db, RH, P_atm=101.325):
#     P_sat = saturation_vapor_pressure(T_db)
#     P_v = RH * P_sat
#     W = 0.622 * P_v / (P_atm - P_v)
#     h = 1.006 * T_db + W * (2501 + 1.805 * T_db)
#     return h
#
#
# def water_enthalpy_liquid(T):
#     c_p_liquid = 4.18
#     h_liquid = c_p_liquid * T
#     return h_liquid
#
#
# h_r = air_enthalpy(data["ACU_Return_Temp"], data["ACU_Return_RH"]/100)
# h_s = air_enthalpy(data["ACU_Supply_Temp"], data["ACU_Supply_RH"]/100)
# h_air_dif = (h_r - h_s) * data["FCU_air_mass_flowrate"] * 1.29
# energy_dif = (data["FCU_air_mass_flowrate"] * 1.29 * 1005 * (data["ACU_Return_Temp"] - data["ACU_Supply_Temp"]))/1000
# power_load = (data["ITE_load"] + data["W"]) / 1000
# print(f"Power load: {power_load} kJ")
# print(f"Air enthalpy difference: {h_air_dif:.2f} kJ")
# print(f"Air energy Difference: {energy_dif:.2f} kJ")
#
# h_water_s = water_enthalpy_liquid(data["chws_temperature"])
# h_water_r = water_enthalpy_liquid(data["chwr_temperature"])
# h_water_dif_rate = (h_water_r - h_water_s)
# water_mass_flow = energy_dif / h_water_dif_rate * 60 * 60 / 1000
# print(f"Water mass flow rate: {water_mass_flow:.2f} m3/h")
