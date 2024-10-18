from loguru import logger
from dotmap import DotMap
from CoolProp.CoolProp import PropsSI


class Chiller:
    def __init__(self, ref_capacity, ref_cop, min_part_load_ratio, max_part_load_ratio):

        self.ref_capacity = ref_capacity
        self.ref_cop = ref_cop
        self.min_part_load_ratio = min_part_load_ratio
        self.max_part_load_ratio = max_part_load_ratio

        self.chiller_cap_ft_coe = [2.521130e-01, 1.324053e-02, -8.637329e-03, 8.581056e-02, -4.261176e-03, 8.661899e-03]
        self.chiller_eir_plr_coe = [2.778889e-01, 2.338363e-01, 4.883748e-01]
        self.chiller_eir_ft_coe = [4.475238e-01, -2.588210e-02, -1.459053e-03, 4.342595e-02, -1.000651e-03, 1.920106e-03]
        self.cp_water_default = 4200

        logger.info(f"Chiller initialized. Reference capacity: {self.ref_capacity}. Reference cop: {self.ref_cop}.")

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

    def run_chiller(self, chw_flow_rate, evapora_inlet_temp, evapora_outlet_temp, condenser_inlet_temp,
                    condenser_inlet_mass):

        Cp_inlet = self.get_fluid_property(fluid_name="water",
                                           temperature=evapora_inlet_temp,
                                           property_type="specific_heat")

        Cp_outlet = self.get_fluid_property(fluid_name="water",
                                            temperature=evapora_outlet_temp,
                                            property_type="specific_heat")

        actual_load = chw_flow_rate * (evapora_inlet_temp * Cp_inlet - evapora_outlet_temp * Cp_outlet)

        chiller_cap_ft = (self.chiller_cap_ft_coe[0] + self.chiller_cap_ft_coe[1] * evapora_outlet_temp +
                          self.chiller_cap_ft_coe[2] * evapora_outlet_temp ** 2 + self.chiller_cap_ft_coe[3] *
                          condenser_inlet_temp + self.chiller_cap_ft_coe[4] * condenser_inlet_temp ** 2
                          + self.chiller_cap_ft_coe[5] * evapora_outlet_temp * condenser_inlet_temp)

        avail_chiller_capacity = self.ref_capacity * chiller_cap_ft

        part_load_ratio = max(0.0, min(abs(actual_load/avail_chiller_capacity), self.max_part_load_ratio))
        logger.info(f"part load ratio of the chiller: {part_load_ratio}")

        if part_load_ratio >= self.max_part_load_ratio:
            logger.warning("Max part load ratio reached")

        chiller_eir_ft = (self.chiller_eir_ft_coe[0] + self.chiller_eir_ft_coe[1] *
                          evapora_outlet_temp + self.chiller_eir_ft_coe[2] *
                          evapora_outlet_temp ** 2 + self.chiller_eir_ft_coe[3] *
                          condenser_inlet_temp + self.chiller_eir_ft_coe[4] * condenser_inlet_temp ** 2
                          + self.chiller_eir_ft_coe[5] * evapora_outlet_temp * condenser_inlet_temp)

        if part_load_ratio < self.min_part_load_ratio:
            frac = min(1.0, (part_load_ratio/self.min_part_load_ratio))
        else:
            frac = 1.0

        chiller_eir_f_plr = (self.chiller_eir_plr_coe[0] + self.chiller_eir_plr_coe[1] * part_load_ratio +
                             self.chiller_eir_plr_coe[2] * part_load_ratio ** 2)

        chiller_power = (avail_chiller_capacity / self.ref_cop) * chiller_eir_f_plr * chiller_eir_ft * frac
        cop_run = actual_load / chiller_power
        logger.info(f"Chiller actual COP: {cop_run}")

        condenser_leave_temp = actual_load / self.cp_water_default / condenser_inlet_mass + condenser_inlet_temp

        return DotMap(dict(actual_chiller_load=actual_load,
                           chiller_power=chiller_power,
                           acutal_chiller_cop=cop_run,
                           condenser_leave_temp=condenser_leave_temp))
