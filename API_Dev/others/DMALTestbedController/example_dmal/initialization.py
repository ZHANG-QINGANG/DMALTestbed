import os.path
from pathlib import Path
import yaml
from dotmap import DotMap
from dclib import Building
from dctwin.third_parties import IDFBuilder, ConfigBuilder
from twinupdater.runner.extract_param import Extract
from loguru import logger
from dctwin.registraion import make_env
import numpy as np


class Initialization:
    def __init__(self, config_file, generate_feature_file=True, generate_param_file=True):
        self.config_file = config_file
        self.generate_feature_file = generate_feature_file
        self.generate_param_file = generate_param_file

    def generate_idf(self):
        # Build IDF file
        building = Building.load(self.config_file.building_json_path)
        manager = IDFBuilder(
            building=building,
        )
        manager.make()
        device_his_map = self.config_file.device_his_map if self.generate_feature_file else None
        manager.save(
            idf_save_path=self.config_file.idf_path_original,
            device_key_map_save_path=self.config_file.device_key_map,
            device_his_map_save_path=device_his_map,
        )

        manager.save(
            idf_save_path=self.config_file.idf_path_run,
            device_key_map_save_path=self.config_file.device_key_map,
            device_his_map_save_path=device_his_map,
        )

        # Build config file
        config = ConfigBuilder(
            building=building,
            device_key_map=manager.device_key_map,
        )

        config.make_eplus_env_config(
            idf_file=Path(self.config_file.idf_path_run),
            weather_file=Path(self.config_file.weather_data),
            network="host",
            host="host.docker.internal"
        )
        config.make_cpu_loading_schedules()
        # config.make_chilled_water_loop_supply_temperature_actions(lb=10, ub=15, normalize_method=True)
        # config.make_chilled_water_pump_flow_rates_actions(lb=50, ub=180, normalize_method=True)
        # config.make_acu_supply_air_temperature_actions()
        # config.make_acu_supply_air_flow_rate_actions()
        config.make_chilled_water_loop_observations(exposed=False)
        config.make_acu_fan_observations(exposed=False)
        config.make_cooling_coil_observations(exposed=False)
        config.make_pump_observations(exposed=False)
        config.make_chiller_observations(exposed=False)
        config.make_cooling_tower_observations(exposed=False)
        config.make_zone_observations(exposed=False)
        config.make_ite_observations(exposed=False)
        config.save(path=self.config_file.engine_config)

    def generate_params(self):
        if self.generate_param_file:
            extractor = Extract(self.config_file)
            extractor.extract_params()
            logger.info("generate parameter file successfully...")
        else:
            if os.path.exists(self.config_file.extract_param_path):
                logger.info("parameter file existed, pass...")
            else:
                raise ValueError("parameter file not existed, set generate_param_file=True...")

    def run(self):
        env = make_env(env_proto_config=self.config_file.engine_config, reward_fn=lambda x: 0.0)
        env.reset()
        done = False
        try:
            while not done:
                act = np.array(self.config_file.control_action)
                obs, rew, done, truncated, info = env.step(act)
        except Exception as e:
            logger.error(f"Run DCTwin Failed... {e}")
        env.close()


def main():
    with open('configs/updater_config.yaml', 'r') as file:
        data = yaml.safe_load(file)
    config_file = DotMap(data)
    initialization = Initialization(config_file, generate_feature_file=True, generate_param_file=True)
    initialization.generate_idf()
    # initialization.generate_params()
    initialization.run()


if __name__ == "__main__":
    main()

