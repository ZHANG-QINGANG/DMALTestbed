from TwinUpdater.twinupdater import TwinUpdater
from dotmap import DotMap
import yaml
import numpy as np

with open('configs/updater_config.yaml', 'r') as file:
    data = yaml.safe_load(file)

# define path
info = DotMap(dict(data))

# run
twin_up = TwinUpdater()

# load configurations
user_config = twin_up.load(info=info)
user_config.control_action = np.array(user_config.control_action)

# run simulation
twin_up.run(user_config=user_config)
