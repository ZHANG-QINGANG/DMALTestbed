from CoolProp.CoolProp import PropsSI
import numpy as np
from parameterCalculation import NTUHE, nusseltCoefficient, nusseltNumberIn
from mealpy import FloatVar, AEO
import pandas as pd
import torch


class CoolingCoil:

    def __init__(
            self,
            params: dict,
    ):
        super().__init__()
        self.tube_diameter = params["tubeDiameter"]
        self.tube_length = params["tubeLength"]
        self.tube_thickness = params["tubeThickness"]
        self.num_row = params["numberRows"]
        self.num_transverse = params["transverseNumber"]
        self.row_pitch = params["rowPitch"]
        self.transverse_pitch = params["transversePitch"]
        self.tube_roughness = params["tubeRoughness"]
        self.tube_kappa = params["thermalConductivity"]
        self.H_he = self.num_row * self.transverse_pitch + 2 * self.tube_diameter
        self.standard_atomos_pressure = 101325

    def collect(self):
        pass

    def learn(self):
        pass

    def forward(
        self,
        T_air_in,
        m_air,
        T_water_in,
        m_water
    ):
        # fluid properties
        rho_i = PropsSI(
            'D', 'P', self.standard_atomos_pressure, 'T', T_water_in + 273.15, "water"
        )
        Cp_i = PropsSI(
            'C', 'P', self.standard_atomos_pressure, 'T', T_water_in + 273.15, "water"
        )
        k_i = PropsSI(
            'CONDUCTIVITY', 'P', self.standard_atomos_pressure, 'T', T_water_in + 273.15, "water"
        )
        miu_i = PropsSI(
            'V', 'P', self.standard_atomos_pressure, 'T', T_water_in + 273.15, "water"
        )
        Pr_i = PropsSI(
            'PRANDTL', 'P', self.standard_atomos_pressure, 'T', T_water_in + 273.15, "water"
        )
        rho_o = PropsSI(
            'D', 'P', self.standard_atomos_pressure, 'T', T_air_in + 273.15, "air"
        )
        Cp_o = PropsSI(
            'C', 'P', self.standard_atomos_pressure, 'T', T_air_in + 273.15, "air"
        )
        k_o = PropsSI(
            'CONDUCTIVITY', 'P', self.standard_atomos_pressure, 'T', T_air_in + 273.15, "air"
        )
        miu_o = PropsSI(
            'V', 'P', self.standard_atomos_pressure, 'T', T_air_in + 273.15, "air"
        )
        Pr_o = PropsSI(
            'PRANDTL', 'P', self.standard_atomos_pressure, 'T', T_air_in + 273.15, "air"
        )

        # tube inside
        v_water = m_water / rho_i  # internal fluid volumetric flow rate
        u_i = v_water / (self.num_row * self.num_transverse) / (np.pi / 4 * self.tube_diameter ** 2)
        Re_i = rho_i * u_i * self.tube_diameter / miu_i  # internal fluid Reynolds number
        rr_i = self.tube_roughness / self.tube_diameter  # relative roughness
        fr, nu_i = nusseltNumberIn(rr_i, Re_i, Pr_i)  # friction factor and Nusselt number
        h_i = nu_i * k_i / self.tube_diameter  # internal fluid heat transfer coefficient

        dP_i = fr * (self.tube_length / self.tube_diameter) * (rho_i * u_i ** 2) / 2  # internal fluid pressure drop
        pump_power_i = (self.num_row * self.num_transverse) * dP_i * (m_water / rho_i)  # internal fluid pumping power

        # tube outside
        u_o = m_air / rho_o / (self.tube_length * self.H_he)  # external fluid velocity
        u_omax = self.transverse_pitch / (self.transverse_pitch - self.tube_diameter) * u_o
        Re_omax = rho_o * u_omax * self.tube_diameter / miu_o  # maximum external fluid Reynolds number
        coef1, expo1 = nusseltCoefficient(Re_omax)  # coefficient and exponent of Nusselt number
        Nu_o = coef1 * (Re_omax ** expo1) * (Pr_o ** 0.36)  # external fluid Nusselt number
        # correct the outside Nusselt number when the row number is less than 20
        if self.num_row < 20:
            N_list = np.array([1, 2, 3, 4, 5, 7, 10, 13, 16])  # row number list
            N_list = abs(N_list - np.array(self.num_row))  # difference between row number and row number list
            coef2_list = [0.7, 0.8, 0.86, 0.9, 0.92, 0.95, 0.97, 0.98, 0.99]  # correction coefficient list
            min_id = np.where(N_list == np.min(N_list))[0]  # minimum difference id
            coef2 = coef2_list[min_id[0]]  # correction coefficient
            Nu_o = Nu_o * coef2  # corrected external fluid Nusselt number
        h_o = Nu_o * k_o / self.tube_diameter  # external fluid heat transfer coefficient

        f_o = 0.2  # external fluid friction factor
        dP_o = self.num_row * (rho_o * u_omax ** 2 / 2) * f_o  # external fluid pressure drop
        pump_power_o = dP_o * (m_air / rho_o)  # external fluid pumping power

        # pumping power, U value and NTU value
        pump_power = pump_power_i + pump_power_o  # W, pumping power
        U = 1 / (
            1 / h_i + 1 / h_o + np.log((self.tube_thickness + self.tube_diameter) / self.tube_diameter) *
            self.tube_diameter / self.tube_kappa
        )  # W/m2K, overall heat transfer coefficient
        A = self.num_transverse * self.num_row * (np.pi * self.tube_diameter * self.tube_length)

        C_i = m_water * Cp_i  # W/K, internal fluid heat capacity
        C_o = m_air * Cp_o  # W/K, external fluid heat capacity
        C_min = min(C_i, C_o)  # W/K, minimum heat capacity
        eff, NTU = NTUHE(C_i, C_o, U, A)  # efficiency and number transfer unit of heat exchanger
        Q_max = C_min * (T_air_in - T_water_in)  # W, maximum heat transfer
        heat_transfer_rate = eff * Q_max - pump_power  # W, heat transfer
        T_air_out = T_air_in - heat_transfer_rate / C_o  # degree C, external fluid outlet temperature
        T_water_out = T_water_in + (heat_transfer_rate + pump_power) / C_i
        if pump_power / heat_transfer_rate > 0.1:
            print("Pump power is too high")
        return T_water_out, T_air_out, NTU, eff, heat_transfer_rate, pump_power


def coil_predict(T_air_in, m_air, T_water_in, m_water):
    model = CoolingCoil(
        params=params
    )

    Tw_out, Ta_out, NTU, eff, Q, power = model.forward(
        T_air_in=T_air_in,
        m_air=m_air,
        T_water_in=T_water_in,
        m_water=m_water
    )

    return Tw_out, Ta_out, NTU, eff, Q, power


Tw_out, Ta_out, NTU, eff, Q, power = coil_predict(T_air_in=22.7, m_air=1.37, T_water_in=9.2, m_water=0.2)
print(f"Tw_out: {Tw_out}. Ta_out: {Ta_out}. NTU: {NTU}. eff: {eff}. Q: {Q}. power: {power}")


def calibration():
    his_data = pd.read_csv("./H")



if __name__ == "__main__":
    import matplotlib.pyplot as plt

    params = {
        "tubeDiameter": 0.05,
        "tubeLength": 1,
        "tubeThickness": 0.002,
        "tubeRoughness": 1e-5,
        "numberRows": 20,
        "rowPitch": 0.02,
        "transverseNumber": 6,
        "transversePitch": 0.03,
        "material": "copper",
        "thermalConductivity": 400
    }

    model = CoolingCoil(
        params=params
    )


    def objective_function(x):
        load = 2300
        with torch.no_grad():
            Tw_out, Ta_out, NTU, eff, Q, power = model.forward(
                                                                T_air_in=torch.tensor(21.6),
                                                                m_air=torch.tensor(1.7),
                                                                T_water_in=torch.tensor(10.0),
                                                                m_water=torch.tensor(x)  # 20.7% ~ 0.05
                                                               )
        error = abs(Q - load).detach().cpu().numpy()[0]
        return error


    problem_dict = {
        "bounds": FloatVar(lb=(0.,) * 1, ub=(1.,) * 1, name="delta"),
        "minmax": "min",
        "obj_func": objective_function
    }

    optimizer = AEO.AugmentedAEO(epoch=50, pop_size=50)
    g_best = optimizer.solve(problem_dict)
    print(f"Solution: {g_best.solution}, Fitness: {g_best.target.fitness}")
    print(f"Solution: {optimizer.g_best.solution}, Fitness: {optimizer.g_best.target.fitness}")

