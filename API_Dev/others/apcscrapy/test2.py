import time
import requests
from threading import Thread
from run import run_everything

# 在新线程中启动 Flask 应用
server_thread = Thread(target=run_everything)
server_thread.start()

# 等待 Flask 应用启动
time.sleep(2)

# 发送请求到 Flask 应用
try:
    response = requests.get('http://0.0.0.0:1115/get_data')
    if response.status_code == 200:
        print("Server started successfully")
        print(f"Response: {response.json()}")
except requests.ConnectionError as e:
    print(f"Error connecting to server: {e}")

# 发送关闭请求，优雅地关闭 Flask 应用
try:
    shutdown_response = requests.post('http://0.0.0.0:1115/shutdown')
    print("Shutdown response:", shutdown_response.text)
except requests.ConnectionError as e:
    print(f"Error shutting down the server: {e}")

# 等待 Flask 服务器线程退出
server_thread.join()
