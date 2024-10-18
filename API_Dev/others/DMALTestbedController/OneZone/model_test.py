import json
from dctwin.data import Batch
from dclib import Building
from dctwin.managers import HVACManager
from dctwin.utils import read_engine_config

engine_config = read_engine_config("configs/dt/dctwin.prototxt")

with open("configs/dt/example.json", "r") as f:
    device_key_mapping = json.load(f)

building = Building.load("models/example.json")

acts = [0.2, 1, 22, 4, 27, 14,]
external_inputs = {
    "outdoor_temperature": 27.,
}

manager = HVACManager(
    config=engine_config,
    building=building,
    device_key_mapping=device_key_mapping
)
manager.reset()
format_acts: Batch = manager.format_actions(acts)
format_inps: Batch = manager.format_external_inputs(external_inputs)

manager.run(
    acts=format_acts,
    obs=None,
    inps=format_inps
)

power = manager.data.obs_next.dc.facility_power
power.backward(retain_graph=True)
print(manager.data)
print(manager.acts_require_grad)
print(manager.acts_require_grad.grad)
