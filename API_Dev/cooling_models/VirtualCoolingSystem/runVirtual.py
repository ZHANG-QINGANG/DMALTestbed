from chiller import Chiller
from pumps import Pump
from condenserLoopTowers import CalculateVariableSpeedTower
from dotmap import DotMap
from CoolProp.CoolProp import PropsSI
from loguru import logger


class VirtualCoolingSystem:
    def __init__(self):
        tower_config_spec = DotMap({
            "modelType": "YorkCalcUserDefined",
            "modelCoefficientName": "YorkCalc Default Tower Model",
            "designInletAirWetBulbTemperature": 26.6,
            "designApproachTemperature": 5,
            "designRangeTemperature": 5,
            "designWaterFlowRate": 0.005,  # m3/s
            "designAirFlowRate": 4.0,  # m3/s
            "designFanPower": 2000,
            "minimumAirFlowRateRatio": 0.25,
            "fractionOfTowerCapacityInFreeConvectionRegime": 0,
            "basinHeaterCapacity": 0,
            "basinHeaterSetpointTemperature": 2.0,
            "evaporationLossMode": "LossFactor",
            "evaporationLossFactor": 0.2,
            "driftLossPercent": 0.008,
            "blowdownCalculationMode": "ConcentrationRatio",
            "blowdownConcentrationRatio": 3,
            "numberOfCells": 1,
            "cellControl": "MinimalCell",
            "cellMinimumWaterFlowRateFraction": 0.33,
            "cellMaximumWaterFlowRateFraction": 1.0,
            "sizingFactor": 1
        })

        chwp_config_spec = DotMap(dict(pump_power_curve_coe=[0, 1, 0, 0], m_design=1.0, power_design=1800))
        cwp_config_spec = DotMap(dict(pump_power_curve_coe=[0, 1, 0, 0], m_design=5.0, power_design=1800))
        chiller_config_spec = DotMap(dict(ref_capacity=14000, ref_cop=5.89, min_part_load_ratio=0.1,
                                          max_part_load_ratio=1.15))

        self.chwp = Pump(pump_power_curve_coe=chwp_config_spec.pump_power_curve_coe,
                         m_design=chwp_config_spec.m_design, power_design=chwp_config_spec.power_design,
                         name="CHWP")

        self.cwp = Pump(pump_power_curve_coe=cwp_config_spec.pump_power_curve_coe, m_design=cwp_config_spec.m_design,
                        power_design=cwp_config_spec.power_design, name="CWP")

        self.chiller = Chiller(ref_capacity=chiller_config_spec.ref_capacity, ref_cop=chiller_config_spec.ref_cop,
                               min_part_load_ratio=chiller_config_spec.min_part_load_ratio,
                               max_part_load_ratio=chiller_config_spec.max_part_load_ratio)

        self.tower = CalculateVariableSpeedTower(tower_config_spec)

    @staticmethod
    def get_fluid_property(fluid_name, temperature, property_type):
        try:
            # Convert temperature to Kelvin
            temperature_K = temperature + 273.15  # Assuming input temperature is in Celsius

            # Define property mapping
            property_map = {
                'density': 'D',
                'specific_heat': 'C'
            }

            # Check if the property type is valid
            if property_type not in property_map:
                raise ValueError(f"Invalid property type: {property_type}")

            # Get the property
            prop = PropsSI(property_map[property_type], 'T', temperature_K, 'P', 101325, fluid_name)

            return prop
        except ValueError as e:
            logger.error(f"Error: {e:.2f}")
            return None

    def run(self, chw_vol_flow_rate, chw_sup_temp, chw_return_temp, condenser_inlet_temp=30, condenser_inlet_mass=4,
            ambient_temp=27.0):

        sim_results = DotMap(dict())

        chw_water_density = self.get_fluid_property(fluid_name="water",
                                                    temperature=chw_sup_temp,
                                                    property_type="density")

        chw_mass_flow_rate = chw_vol_flow_rate * chw_water_density

        chwp_results = self.chwp.run(m_water=chw_mass_flow_rate)
        sim_results.update(chwp_results)

        chiller_results = self.chiller.run_chiller(chw_flow_rate=chw_mass_flow_rate, evapora_outlet_temp=chw_sup_temp,
                                                   evapora_inlet_temp=chw_return_temp,
                                                   condenser_inlet_mass=condenser_inlet_mass,
                                                   condenser_inlet_temp=condenser_inlet_temp)
        sim_results.update(chiller_results)

        cwp_results = self.cwp.run(m_water=condenser_inlet_mass)
        sim_results.update(cwp_results)

        tower_results = self.tower.run(WaterMassFlowRate=condenser_inlet_mass,
                                       Node_WaterInletNodeTemp=chiller_results.condenser_leave_temp,
                                       AirWetBulb=ambient_temp,
                                       TempSetPoint=condenser_inlet_temp)
        sim_results.update(tower_results)

        return sim_results


if __name__ == '__main__':
    virtual_cooling_system = VirtualCoolingSystem()
    simulation_results = virtual_cooling_system.run(chw_vol_flow_rate=4.2e-5,
                                                    chw_sup_temp=8.5,
                                                    chw_return_temp=22,
                                                    condenser_inlet_temp=30,
                                                    condenser_inlet_mass=1,
                                                    ambient_temp=27.0)
    print(simulation_results)
