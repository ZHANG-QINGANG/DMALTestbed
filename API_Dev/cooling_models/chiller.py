import numpy as np


class Chiller:
    def __init__(self, ref_capacity, ref_cop, min_part_load_ratio, max_part_load_ratio):

        self.ref_capacity = ref_capacity
        self.ref_cop = ref_cop
        self.min_part_load_ratio = min_part_load_ratio
        self.max_part_load_ratio = max_part_load_ratio

        self.chiller_cap_ft_coe = [2.521130e-01, 1.324053e-02, -8.637329e-03, 8.581056e-02, -4.261176e-03, 8.661899e-03]
        self.chiller_eir_plr_coe = [2.778889e-01, 2.338363e-01, 4.883748e-01]
        self.chiller_eir_ft_coe = [4.475238e-01, -2.588210e-02, -1.459053e-03, 4.342595e-02, -1.000651e-03, 1.920106e-03]
        self.cp_water = 4200  # J/Kg
        self.condenser_inlet_temp = 30
        self.cw_flow_rate = 0.6
        self.chwp_coe = [0, 1, 0, 0]
        self.chwp_m_water_design = 0.98
        self.chwp_power_design = 1800

    def chwp_power_cal(self, m_water):
        plr = m_water / self.chwp_m_water_design
        fraction_full_load_power = (self.chwp_coe[0] + self.chwp_coe[1] * plr + self.chwp_coe[2] * plr ** 2 +
                                    self.chwp_coe[3] * plr ** 3)
        chwp_power = fraction_full_load_power * self.chwp_power_design
        return chwp_power

    def cwp_power_cal(self, m_water):
        plr = m_water / self.chwp_m_water_design
        fraction_full_load_power = (self.chwp_coe[0] + self.chwp_coe[1] * plr + self.chwp_coe[2] * plr ** 2 +
                                    self.chwp_coe[3] * plr ** 3)
        cwp_power = fraction_full_load_power * self.chwp_power_design
        return cwp_power

    def run_chiller(self, chw_flow_rate, evapora_inlet_temp, evapora_outlet_temp):

        my_load = chw_flow_rate * (evapora_inlet_temp - evapora_outlet_temp) * self.cp_water
        chiller_cap_ft = (self.chiller_cap_ft_coe[0] + self.chiller_cap_ft_coe[1] *
                          evapora_outlet_temp + self.chiller_cap_ft_coe[2] *
                          evapora_outlet_temp ** 2 + self.chiller_cap_ft_coe[3] *
                          self.condenser_inlet_temp + self.chiller_cap_ft_coe[4] * self.condenser_inlet_temp ** 2
                          + self.chiller_cap_ft_coe[5] * evapora_outlet_temp *
                          self.condenser_inlet_temp)

        print(f"chiller_cap_ft {chiller_cap_ft}")

        avail_chiller_capacity = self.ref_capacity * chiller_cap_ft

        part_load_ratio = max(0.0, min(abs(my_load/avail_chiller_capacity), self.max_part_load_ratio))
        print(f"part load ratio: {part_load_ratio}")

        if part_load_ratio >= self.max_part_load_ratio:
            print("Max part load ratio reached")

        chiller_eir_ft = (self.chiller_eir_ft_coe[0] + self.chiller_eir_ft_coe[1] *
                          evapora_outlet_temp + self.chiller_eir_ft_coe[2] *
                          evapora_outlet_temp ** 2 + self.chiller_eir_ft_coe[3] *
                          self.condenser_inlet_temp + self.chiller_eir_ft_coe[4] * self.condenser_inlet_temp ** 2
                          + self.chiller_eir_ft_coe[5] * evapora_outlet_temp *
                          self.condenser_inlet_temp)

        if part_load_ratio < self.min_part_load_ratio:
            frac = min(1.0, (part_load_ratio/self.min_part_load_ratio))
        else:
            frac = 1.0

        chiller_eir_f_plr = (self.chiller_eir_plr_coe[0] + self.chiller_eir_plr_coe[1] * part_load_ratio +
                             self.chiller_eir_plr_coe[2] * part_load_ratio ** 2)

        chiller_power = (avail_chiller_capacity / self.ref_cop) * chiller_eir_f_plr * chiller_eir_ft * frac
        cop_run = my_load / chiller_power

        condenser_leave_temp = my_load / self.cp_water / self.cw_flow_rate + self.condenser_inlet_temp
        chwp_power_cal = self.chwp_power_cal(chw_flow_rate)
        cwp_power_cal = self.cwp_power_cal(self.cw_flow_rate)

        return my_load, chiller_power, cop_run, condenser_leave_temp, chwp_power_cal, cwp_power_cal


chiller = Chiller(ref_capacity=14000, ref_cop=5.89, min_part_load_ratio=0.1, max_part_load_ratio=1.15)

my_load, power, cop_actual, condenser_leave_temp, chwp_power_cal, cwp_power_cal = chiller.run_chiller(chw_flow_rate=0.17, evapora_outlet_temp=11, evapora_inlet_temp=15.5)

print(f"my load: {my_load}. chiller power: {power}. cop actual: {cop_actual}. "
      f"condenser leave_temp: {condenser_leave_temp}. chwp_power_cal: {chwp_power_cal}. cwp_power_cal: {cwp_power_cal}")





























