import subprocess
import time
import requests

# 启动 Flask 应用，指定路径为 apcscrapy 文件夹下的 flask_app.py
process = subprocess.Popen(['python3', 'run.py'])

# 给应用程序一些时间来启动
time.sleep(2)



# 可在需要时终止 Flask 应用
# process.terminate()
