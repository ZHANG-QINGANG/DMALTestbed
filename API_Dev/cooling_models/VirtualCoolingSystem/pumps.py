from loguru import logger
from dotmap import DotMap


class Pump:
    def __init__(self, pump_power_curve_coe, m_design, power_design, name):
        """
        :param pump_power_curve_coe: pump power curve coe
        :param m_design: design water mass flow rate [kg/s]
        :param power_design: design pump power [W]
        """
        self.coe = pump_power_curve_coe
        self.m_design = m_design
        self.power_design = power_design
        self.name = name

        logger.info(f"Pump {self.name} initialized. Design water mass flow rate: {self.m_design} [Kg/s]."
                    f"Design pump power: {self.power_design} [W]")

    def run(self, m_water):
        plr = m_water / self.m_design
        fraction_full_load_power = self.coe[0] + self.coe[1] * plr + self.coe[2] * plr ** 2 + self.coe[3] * plr ** 3
        power = fraction_full_load_power * self.power_design

        logger.info(f"Pump {self.name} calculated power: {power}")

        return DotMap({f"{self.name}_power": power})
