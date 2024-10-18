import gym
from gym import spaces
import requests
import json
import numpy as np
from loguru import logger
import csv
import os


class AirConditionerEnv(gym.Env):
    """Custom Environment that follows OpenAI Gym interface"""

    def __init__(self):
        super(AirConditionerEnv, self).__init__()
        # Define action and observation space
        self.action_space = spaces.Box(
            low=np.array([0, 0]),
            high=np.array([1, 3]),
            dtype=np.float32
        )

        # Observation space
        # Assuming the observation includes the temperature and humidity
        self.observation_space = spaces.Box(
            low=np.array([15.0, 0.0]),
            high=np.array([40.0, 100]),
            dtype=np.float32
        )

        # URL for reading and writing data
        self.url = 'http://10.96.182.179:5000/airconditioner'
        # Initialize state
        self.state = None

    def reset(self):
        """
        Reset the state of the environment to an initial state
        """
        self._send_control_action([0, 3])
        state = self._get_state_from_server()
        return state

    def step(self, action):
        """
        Execute one time step within the environment
        """

        # Get new state after action
        self.state = self._get_state_from_server()

        # Send the action to the server
        self._send_control_action(action)

        # Calculate the reward, for example based on how close we are to a target temperature
        reward = self._calculate_reward(self.state)

        # Define if the episode is done
        done = False  # You can define a condition to stop the episode

        # Optionally we can pass additional info
        info = {}

        return np.array(self.state), reward, done, info, None

    def render(self, close=False):
        """
        Render the environment to the screen (optional)
        """
        # This function could be used to print the state in a human-readable form
        logger.info(f"State: {self.state}")

    def close(self):
        """
        Clean up and close the environment
        """
        pass

    def _get_state_from_server(self):
        """
        Helper function to get the current state of the system from the server
        """
        response = requests.get(self.url)
        if response.status_code == 200:
            data = response.json()
            state = [
                data['data']['room_temperature_1'],
                data['data']['room_humidity_1'],
            ]
            return state
        else:
            raise Exception(f"Failed to get data, status code: {response.status_code}")

    def _send_control_action(self, action):
        """
        Helper function to send control action to the server
        """
        # Example action: [room_temperature_setpoint, valve_ovr_cmd, fcu_speed_ovr_cmd]
        data = {
            "room_temperature_setpoint": 23.0,  # default 23
            "valve_ovr_flag": int(action[0]),  # Assuming PID controller is activated
            "valve_ovr_cmd": 10.0,  # valve opening
            "fcu_ss_ovr_flag": 0,  # Assuming override is always not enabled
            "fcu_ss_ovr_cmd": 0,  # Assuming fcu_ss_cmd is start (0)
            "fcu_speed_ovr_flag": 1,  # Assuming override is always enabled
            "fcu_speed_ovr_cmd": int(action[1]),  # FCU fan speed 1, 2, 3
        }
        json_data = json.dumps(data)
        response = requests.post(self.url, data=json_data, headers={'Content-Type': 'application/json'})

        if response.status_code != 200:
            raise Exception(f"Failed to send control action, status code: {response.status_code}")
        else:
            logger.info(f"Successfully sent control action")

    def _calculate_reward(self, state):
        """
        Helper function to calculate the reward based on the current state
        """
        # Example: Reward is based on how close the room temperature is to 22 degrees
        target_temperature = 23.0
        current_temperature = state[0]

        # Simple reward: Negative absolute difference from target
        reward = -abs(target_temperature - current_temperature)
        return reward

    def _log_to_csv(self, state, reward):
        """
        Helper function to log state and reward to a CSV file
        """
        pass
