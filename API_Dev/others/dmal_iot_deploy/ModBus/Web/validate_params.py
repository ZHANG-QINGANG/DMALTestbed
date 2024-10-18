

schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Air Conditioner",
    "description": "Air Conditioner",
    "type": "object",
    "properties": {
        "room_temperature_setpoint": {
            "type": "number"
        },
        "valve_ovr_flag": {
            "type": "integer",
            "minimum": 0,
            "maximum": 1,
        },
        "valve_ovr_cmd": {
            "type": "number",
        },
        "fcu_ss_ovr_flag": {
            "type": "integer",
            "minimum": 0,
            "maximum": 1,
        },
        "fcu_ss_ovr_cmd": {
            "type": "integer",
            "minimum": 0,
            "maximum": 1,
        },
        "fcu_speed_ovr_flag": {
            "type": "integer",
            "minimum": 0,
            "maximum": 1,
        },
        "fcu_speed_ovr_cmd": {
            "type": "integer",
            "minimum": 1,
            "maximum": 3,
        },
    },
}
