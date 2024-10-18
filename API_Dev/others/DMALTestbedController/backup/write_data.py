# import requests
# import json
#
# # 目标URL
# url = 'http://10.96.182.179:5000/airconditioner'
#
# # 要写入的数据
# data = {
#     "room_temperature_setpoint": 23.0,
#     "valve_ovr_flag": 0,
#     "valve_ovr_cmd": 100.0,
#     "fcu_ss_ovr_flag": 0,
#     "fcu_ss_ovr_cmd": 0,
#     "fcu_speed_ovr_flag": 0,
#     "fcu_speed_ovr_cmd": 3
# }
#
# # 将数据转换为JSON格式
# json_data = json.dumps(data)
#
# # 发送POST请求
# response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})
#
# # 检查请求是否成功
# if response.status_code == 200:
#     print("Data successfully written:", response.json())
# else:
#     print(f"Failed to write data, status code: {response.status_code}")
#
#
