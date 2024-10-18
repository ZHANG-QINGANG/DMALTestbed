import time
from loguru import logger
import numpy as np
from DMALTestbedEnv import AirConditionerEnv
from tensorboardX import SummaryWriter

control = input(f"please confirm whether need to control the system (y/n):")
if control == "n":
    exit(1)

# TensorBoardX setup
log_dir = "logs/room_temperature"
writer = SummaryWriter(log_dir)

# Create and reset the environment
env = AirConditionerEnv()
s_t = env.reset()

action = np.array([0, 3])
step = 0

# Step through the environment
while True:
    if s_t[0] < 24:
        action = np.array([1, 1])
    else:
        action = np.array([0, 3])

    s_t, r_t, done, info, _ = env.step(action)

    logger.info(f"step: {step}. room temperature: {s_t[0]}, action: {action}")

    # Log room temperature to TensorBoardX
    writer.add_scalar('Room Temperature', float(s_t[0]), step)
    writer.add_scalar('Action 0 (Valve Control)', float(action[0]), step)
    writer.add_scalar('Action 1 (Fan Speed Control)', float(action[1]), step)

    step += 1
    time.sleep(30)

# Close the writer when done (or at the end of the script)
writer.close()
