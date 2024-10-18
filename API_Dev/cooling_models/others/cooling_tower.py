import math
from cmath import inf
from CoolProp.CoolProp import HAPropsSI


class RK4:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.param = []

    def getNewValue(self):
        v0 = self.value
        p1 = self.param[0]
        p2 = self.param[1]
        p3 = self.param[2]
        p4 = self.param[3]
        return v0 + (p1 + 2 * p2 + 2 * p3 + p4)/6

class CoolingTowerModel():
    """
    Constant speed cooling tower model that always operates at the maximum capacity.
    """
    def __init__(
        self
    ):
        pass

    def get_j(self, delta_Tw, c_pw, mw_ma, w_ws, w0, i_masw, i_ma_n, Le, i_v, T_w):
        return delta_Tw * c_pw * mw_ma * (w_ws - w0) / (
                    i_masw - i_ma_n + (Le - 1) * (i_masw - i_ma_n - (w_ws - w0) * i_v) - (w_ws - w0) * c_pw * (
                        T_w - 273.15))

    def get_k(self, delta_Tw, c_pw, mw_ma, w_sw, w0, T_w, i_masw, i_ma_0, Le, i_v):
        return delta_Tw * c_pw * mw_ma * (1 + ((w_sw - w0) * c_pw * T_w) / (
                    i_masw - i_ma_0 + (Le - 1) * (i_masw - i_ma_0 - (w_sw - w0) * i_v) - (w_sw - w0) * c_pw * T_w))

    def get_l(self, delta_Tw, c_pw, i_masw, Le, w_sw, i_v, w_0, Tw, i_ma_n):
        return (delta_Tw * c_pw) / (
                    i_masw - i_ma_n + (Le - 1) * (i_masw - i_ma_n - (w_sw - w_0) * i_v) - (w_sw - w_0) * c_pw * Tw)

    # Unsaturated case
    def get_dX_dz(self, baaz, w_s, w, m_a):
        return baaz * (w_s - w) / m_a

    def get_dmw_dz(self, baaz, X_s_w, X):
        return baaz * (X_s_w - X)

    def get_dTa_dz(self, baaz, Le, T_w, T_a, c_pa_a, c_pv_a, c_pv_w, w, w_s, m_a):
        return baaz * (Le * (T_w - T_a) * (c_pa_a + c_pv_a * w) + (c_pv_w * T_w - c_pv_a * T_a) * (w_s - w)) / (
                    m_a * (c_pa_a + c_pv_a * w))

    def get_dTw_dz(self, baaz, Le, T_w, T_a, c_pa_a, c_pv_a, c_pv_w, r_0, X_s, X, m_w, c_w):
        return baaz * (Le * (T_w - T_a) * (c_pa_a + c_pv_a * X) + (r_0 + c_pv_w * T_w - c_w * T_w) * (X_s - X)) / (
                    m_w * c_w)

    def get_dha_dz(self, c_pa_a, w, c_pv_a, dTa_dZ, T_a, dX_dZ):
        return (c_pa_a + w * c_pv_a) * dTa_dZ + (2501598 + c_pv_a * T_a) * dX_dZ

    # Saturated case

    def get_dmw_dz_sat(self, baaz, X_s_w, X_s_a):
        return baaz * (X_s_w - X_s_a)

    def get_dX_dZ_sat(self, baaz, X_s_w, X_s_a, m_a):
        return baaz * (X_s_w - X_s_a) / m_a

    def get_dTa_dZ_sat(self, baaz, m_a, Le, T_a, T_w, X_s_w, r_0, c_pv_w, c_w_a, X, X_s_a, c_pv_a, c_pa_a, dX_dT):
        return - 1 * ((baaz / m_a) * (c_pa_a * Le * (T_a - T_w) - X_s_w * (r_0 + c_pv_w * T_w) + c_w_a * (
                    Le * (T_a - T_w) * (X - X_s_a) + T_a * (X_s_w - X_s_a)) + X_s_a * (
                                                  r_0 + c_pv_a * Le * (T_a - T_w) + c_pv_w * T_w)) / (
                                  c_pa_a + c_w_a * X + dX_dT * (r_0 + c_pv_a * T_a - c_w_a * T_a) + X_s_a * (
                                      c_pv_a - c_w_a)))

    def get_dTw_dZ_sat(self, baaz, r_0, c_pv_w, T_w, c_w_w, X_s_w, X_s_a, Le, T_a, c_pa_a, c_w_a, X, c_pv_a, m_w):
        return baaz * ((r_0 + c_pv_w * T_w - c_w_w * T_w) * (X_s_w - X_s_a) + Le * (T_w - T_a) * (
                    c_pa_a + c_w_a * (X - X_s_a) + c_pv_a * X_s_a)) / (c_w_w * m_w)

    def get_dha_dz_sat(self, c_pv_a, T_a, c_w_a, dX_dTa, w_s_a, dTa_dZ, c_pa_a, w, dX_dZ):
        return ((2501598 + c_pv_a * T_a - c_w_a * T_a) * dX_dTa + w_s_a * (
                    c_pv_a - c_w_a) + c_pa_a + w * c_w_a) * dTa_dZ + c_w_a * T_a * dX_dZ

    def get_Beta_a_Az(self, Me, m_w, H):
        # Heat condoctivity and diffusitivity constant of given cooling tower derived from previously determined Merkel number.
        baaz = Me * m_w / H
        return baaz

    def get_c_pa(self, T):
        # Specific heat capacity of dry air
        return 1.045356 * 10 ** 3 - 3.161783 * 10 ** (-1) * T + 7.083814 * 10 ** (-4) * T ** 2 - 2.705209 * 10 ** (
            -7) * T ** 3

    def get_c_pv(self, T):
        # Specific heat capacity of vapour
        return 1.3605 * 10 ** 3 + 2.31334 * T - 2.46784 * 10 ** (-10) * T ** 5 + 5.91332 * 10 ** (-13) * T ** 6

    def get_c_pw(self, T):
        # Specific heat capacity of water
        return 8.15599 * 10 ** 3 - 2.80627 * 10 * T + 5.11283 * 10 ** (-2) * T ** 2 - 2.17582 * 10 ** (-13) * T ** 6

    def get_p_wv(self, T):
        # Pressure
        return 10 ** (10.79586 * (1 - (273.15 / T)) +
                      5.02808 * math.log(273.15 / T, 10) +
                      1.50474 * 10 ** (-4) * (1 - 10 ** (-8.29692 * (T / 273.15) - 1)) +
                      4.2873 * 10 ** (-4) * ((10 ** (4.76955 * (1 - 273.16 / T))) - 1) + 2.786)

    def get_w_ws(self, p_abs, p_vwb):
        # Humidity ratio for saturated air
        return (0.62509 * p_vwb) / (p_abs - 1.005 * p_vwb)

    def get_i_fgw(self, T):
        # Latent heat of water at 0°C
        return 3.4831814 * 10 ** 6 - 5.8627703 * 10 ** 3 * T + 12.139568 * T ** 2 - 1.40290431 * 10 ** (-2) * T ** 3

    def get_i_v(self, i_fgw, c_pv, T_w):
        # Enthalpy of water vapor at local bulk water temperature
        return i_fgw + c_pv * (T_w - 273.15)

    def get_i_masw(self, c_pa, T, w, i_v):
        # Enthalpy of saturated air at local bulk water temperature
        return c_pa * (T - 273.15) + w * i_v

    def get_Le(self, w_sw, w):
        # Lewis factor of the given intersect
        return 0.865 ** 0.667 * (((w_sw + 0.622) / (w + 0.622) - 1)) / (
            math.log(((w_sw + 0.622) / (w + 0.622)), math.e))

    def get_mv_ma(self, m_wi, m_a, w_i):
        # Mass balance at given intersection
        return m_wi / m_a * (1 - m_a / m_wi * (0.02226 - w_i))

    def getDB(self, Enth, X):
        # Dry bulb temperature of air
        return (Enth / 1000 - 2501 * X) / (1.006 + 1.86 * X) + 273.15

    def getWB(self, X):
        # Wet bulb temperature of air
        return (math.log(X / 0.0039)) / 0.0656 + 273.15

    def get_i_ma(self, c_pv_act, c_pa_act, T_db_act, X_act):
        # Specific enthalpy of humid air
        return c_pa_act * (T_db_act - 273.15) + X_act * (2501598 + c_pv_act * (T_db_act - 273.15))

    def get_w(self, T_wb, T, p_vwb, p_abs):
        # Humidity of air in kg water / kg air
        return (((2501.6 - 2.3263 * (T_wb - 273.15)) /
                 (2501.6 + 1.8577 * (T - 273.15) - 4.184 * (T_wb - 273.15))) *
                ((0.62509 * p_vwb) / (p_abs - 1.005 * p_vwb)) -
                ((1.00416 * (T - T_wb)) / (2501.6 + 1.8577 * (T - 273.15) - 4.184 * (T_wb - 273.15))))

    def get_satT(self, p_v):
        # Temperature of saturated humid air at atmospheric pressure
        return 164.630366 + 1.832295 * 10 ** (-3) * p_v + 4.27215 * 10 ** (
            -10) * p_v ** 2 + 3.738954 * 10 ** 3 * p_v ** (-1) - 7.01204 * 10 ** 5 * p_v ** (-2) + 16.161488 * math.log(
            p_v) - 1.437169 * 10 ** (-4) * p_v * math.log(p_v)

    def get_c_w(self, T):
        return -4 * 10 ** (-8) * (T - 273.15) ** 5 + 1 * 10 ** (-5) * (T - 273.15) ** 4 - 0.0015 * (
                    T - 273.15) ** 3 + 0.0997 * (T - 273.15) ** 2 - 3.2667 * (T - 273.15) + 4219.8

    def getWetBulb(self, RH, T):
        return T * math.atan(0.151977 * (RH + 8.313659) ** 0.5) + math.atan(T + RH) - math.atan(
            RH - 1.676331) + 0.00391838 * RH ** (3 / 2) * math.atan(0.023101 * RH) - 4.686035

    def get_merkel_number(
            self,
            water_inlet_temperature,
            water_outlet_temperature,
            air_inlet_temperature,
            air_humidity_initial,
            water_mass_flow_rate,
            air_mass_flow_rate,
            ambient_pressure
    ):

        water_inlet_temperature = water_inlet_temperature + 273.15
        water_outlet_temperature = water_outlet_temperature + 273.15

        humid_air_enthalpy = self.get_i_ma(
            self.get_c_pv(water_outlet_temperature),
            self.get_c_pa(air_inlet_temperature + 273.15),
            air_inlet_temperature + 273.15,
            air_humidity_initial)

        interval = 10

        humidity = []
        enthalpy = []
        merkel = []
        water_temperature = []
        # initial parameters, X0, H0, Me0, Tw0
        humidity.append(air_humidity_initial)
        enthalpy.append(humid_air_enthalpy)
        merkel.append(0)
        water_temperature.append(water_outlet_temperature)

        station = False

        water_temperature_difference = round((water_inlet_temperature - water_outlet_temperature) / interval, 4)
        for i in range(interval):
            humidity_n = humidity[-1]
            humid_air_enthalpy_n = enthalpy[-1]
            merkel_n = merkel[-1]
            water_temperature_n = water_temperature[-1]

            # Humidity ratio of air
            air_humidity_cache = RK4("j", humidity_n)
            # Enthalpy of air
            air_enthalpy_cache = RK4("k", humid_air_enthalpy_n)
            # Merkel constant of the cooling tower
            merkel_cache = RK4("l", merkel_n)

            water_temperature_initial = water_temperature_n
            water_air_ratio = []
            # calculate j(n+1,1) to l(n+1,4)
            for itr in range(4):  # Runge-Kutta method
                if not station:
                    water_middle_temperature = (water_temperature_n + 273.15) / 2
                    air_capacity = self.get_c_pa(water_middle_temperature)
                    vapor_capacity = self.get_c_pv(water_middle_temperature)
                    water_capacity = self.get_c_pw(water_middle_temperature)
                    vapor_pressure = self.get_p_wv(water_temperature_n)
                    saturation_humidity = self.get_w_ws(ambient_pressure, vapor_pressure)
                    water_latent_heat = self.get_i_fgw(273.15)
                    local_vapor_enthalpy = self.get_i_v(water_latent_heat, vapor_capacity, water_temperature_n)
                    saturation_air_enthalpy = self.get_i_masw(air_capacity, water_temperature_n, saturation_humidity,
                                                              local_vapor_enthalpy)
                    lewis_number = self.get_Le(saturation_humidity, humidity_n)
                    water_to_air = self.get_mv_ma(water_mass_flow_rate, air_mass_flow_rate, humidity_n)
                    water_air_ratio.append(water_to_air)
                    air_humidity = self.get_j(
                        water_temperature_difference,
                        water_capacity,
                        water_to_air,
                        saturation_humidity,
                        humidity_n,
                        saturation_air_enthalpy,
                        humid_air_enthalpy_n,
                        lewis_number,
                        local_vapor_enthalpy,
                        water_temperature_n)
                    air_humidity_cache.param.append(air_humidity)
                    air_enthalpy = self.get_k(
                        water_temperature_difference,
                        water_capacity,
                        water_to_air,
                        saturation_humidity,
                        humidity_n,
                        water_temperature_n - 273.15,
                        saturation_air_enthalpy,
                        humid_air_enthalpy_n,
                        lewis_number,
                        local_vapor_enthalpy)
                    air_enthalpy_cache.param.append(air_enthalpy)
                    merkel_number = self.get_l(
                        water_temperature_difference,
                        water_capacity,
                        saturation_air_enthalpy,
                        lewis_number,
                        saturation_humidity,
                        local_vapor_enthalpy,
                        humidity_n,
                        water_temperature_n - 273.15,
                        humid_air_enthalpy_n)
                    merkel_cache.param.append(merkel_number)
                else:  # saturated station
                    wet_bulb_temperature = self.getWB(humidity[-1])
                    dry_bulb_temperature = self.getDB(enthalpy[-1], humidity[-1])
                    vapor_pressure_wet_bulb = self.get_p_wv(wet_bulb_temperature)
                    saturation_air_humidity_air_temperature = self.get_w(
                        wet_bulb_temperature,
                        self.get_satT(vapor_pressure_wet_bulb),
                        vapor_pressure_wet_bulb,
                        ambient_pressure)
                    water_middle_temperature = (water_temperature_n + 273.15) / 2
                    air_capacity = self.get_c_pa(water_middle_temperature)
                    vapor_capacity = self.get_c_pv(water_middle_temperature)
                    water_capacity = self.get_c_pw(water_middle_temperature)
                    vapor_pressure = self.get_p_wv(water_temperature_n)
                    saturation_humidity = self.get_w_ws(ambient_pressure, vapor_pressure)
                    water_latent_heat = self.get_i_fgw(273.15)
                    local_vapor_enthalpy = self.get_i_v(water_latent_heat, vapor_capacity, water_temperature_n)
                    saturation_air_enthalpy = self.get_i_masw(air_capacity, water_temperature_n, saturation_humidity,
                                                         local_vapor_enthalpy)
                    lewis_number = self.get_Le(saturation_humidity, humidity_n)
                    water_to_air = self.get_mv_ma(water_mass_flow_rate, air_mass_flow_rate, humidity_n)
                    water_air_ratio.append(water_to_air)
                    air_humidity = self.get_j(
                        water_temperature_difference, water_capacity, water_to_air,
                        saturation_humidity, saturation_air_humidity_air_temperature,
                        saturation_air_enthalpy, humid_air_enthalpy_n, lewis_number,
                        local_vapor_enthalpy, water_temperature_n)
                    air_humidity_cache.param.append(air_humidity)
                    air_enthalpy = self.get_k(
                        water_temperature_difference, water_capacity, water_to_air,
                        saturation_humidity, saturation_air_humidity_air_temperature,
                        water_temperature_n - 273.15, saturation_air_enthalpy, humid_air_enthalpy_n,
                        lewis_number, local_vapor_enthalpy)
                    air_enthalpy_cache.param.append(air_enthalpy)
                    merkel_number = self.get_l(
                        water_temperature_difference, water_capacity, saturation_air_enthalpy,
                        lewis_number, saturation_humidity, local_vapor_enthalpy,
                        saturation_air_humidity_air_temperature, water_temperature_n - 273.15,
                        humid_air_enthalpy_n)
                    merkel_cache.param.append(merkel_number)

                if itr == 2:  # The last j, k, l
                    humid_air_enthalpy_n = air_enthalpy_cache.value + air_enthalpy
                    humidity_n = air_humidity_cache.value + air_humidity
                    water_temperature_n = water_temperature_initial + water_temperature_difference
                else:
                    humid_air_enthalpy_n = air_enthalpy_cache.value + air_enthalpy / 2
                    humidity_n = air_humidity_cache.value + air_humidity / 2
                    water_temperature_n = water_temperature_initial + water_temperature_difference / 2

            humidity.append((air_humidity_cache.getNewValue()))
            enthalpy.append((air_enthalpy_cache.getNewValue()))
            merkel.append((merkel_cache.getNewValue()))
            water_temperature.append(water_temperature[-1] + water_temperature_difference)

            if not station:  # Judge if it's saturated
                air_temperature = self.getDB(enthalpy[-1], humidity[-1])
                vapor_pressure = self.get_p_wv(air_temperature)
                saturation_air_humidity_water_temperature = self.get_w_ws(ambient_pressure, vapor_pressure)
                relative_humidity = humidity[-1] / saturation_air_humidity_water_temperature * 100
                wet_bulb_temperature = self.getWetBulb(relative_humidity, (air_temperature - 273.15))
                if wet_bulb_temperature > air_temperature - 273.15:
                    station = True

        return merkel[-1]

    def heat_exchanger_cooling_tower(
            self, merkel_number, water_outlet_temperature, air_inlet_temperature,
            water_mass_flow_rate, air_mass_flow_rate, air_humidity,
            ambient_pressure=101712.27):
        water_latent_heat = 2501598

        water_outlet_temperature = water_outlet_temperature + 273.15
        air_inlet_temperature = air_inlet_temperature + 273.15
        water_mass_flow_rate = water_mass_flow_rate
        air_mass_flow_rate = air_mass_flow_rate
        air_humidity = air_humidity
        ambient_pressure = ambient_pressure

        water_temperature = []
        air_temperature = []
        humidity = []
        water_flow_rate = []
        air_enthalpy = []

        water_temperature.append(water_outlet_temperature)
        air_temperature.append(air_inlet_temperature)
        humidity.append(air_humidity)
        water_flow_rate.append(water_mass_flow_rate)
        air_enthalpy.append(
            self.get_i_ma(
                self.get_c_pv(water_outlet_temperature),
                self.get_c_pa(air_inlet_temperature),
                air_inlet_temperature,
                air_humidity))

        step = 25
        station = False

        for i in range(step):

            water_outlet_temperature = water_temperature[-1]
            air_inlet_temperature = air_temperature[-1]
            air_humidity = humidity[-1]
            water_mass_flow_rate = water_flow_rate[-1]
            humid_air_enthalpy = air_enthalpy[-1]

            water_outlet_temperature_cache = RK4("waterTemp", water_outlet_temperature)
            air_inlet_temperature_cache = RK4("airTemperature", air_inlet_temperature)
            humidity_cache = RK4("Humidity", air_humidity)
            water_mass_flow_rate_cache = RK4("waterFlow", water_mass_flow_rate)
            humid_air_enthalpy_cache = RK4("Enthalpy", humid_air_enthalpy)

            for j in range(4):
                if station == False:
                    diffusivity_constant = (merkel_number / (step)) * water_mass_flow_rate
                    air_capacity_air_temperature = self.get_c_pa(air_inlet_temperature)
                    water_vapor_capacity_water_temperature = self.get_c_pv(water_outlet_temperature)
                    water_vapor_capacity_air_temperature = self.get_c_pv(air_inlet_temperature)
                    water_liquid_capacity_water_temperature = self.get_c_w(water_outlet_temperature)

                    vapor_pressure_water_temperature = self.get_p_wv(water_outlet_temperature)
                    saturation_humidity_ratio = self.get_w_ws(ambient_pressure, vapor_pressure_water_temperature)
                    lewis_number = self.get_Le(saturation_humidity_ratio, air_humidity)

                    water_mass_flow_rate_derivative = self.get_dmw_dz(diffusivity_constant, saturation_humidity_ratio,air_humidity)
                    water_mass_flow_rate_cache.param.append(water_mass_flow_rate_derivative)

                    humidity_derivative = self.get_dX_dz(diffusivity_constant, saturation_humidity_ratio, air_humidity,air_mass_flow_rate)
                    humidity_cache.param.append(humidity_derivative)

                    air_temperature_derivative = self.get_dTa_dz(
                        diffusivity_constant, lewis_number,
                        water_outlet_temperature - 273.15,
                        air_inlet_temperature - 273.15,
                        air_capacity_air_temperature,
                        water_vapor_capacity_air_temperature,
                        water_vapor_capacity_water_temperature, air_humidity,
                        saturation_humidity_ratio, air_mass_flow_rate)
                    air_inlet_temperature_cache.param.append(air_temperature_derivative)

                    water_temperature_derivative = self.get_dTw_dz(
                        diffusivity_constant, lewis_number,
                        water_outlet_temperature - 273.15,
                        air_inlet_temperature - 273.15,
                        air_capacity_air_temperature,
                        water_vapor_capacity_air_temperature,
                        water_vapor_capacity_water_temperature, water_latent_heat,
                        saturation_humidity_ratio, air_humidity,
                        water_mass_flow_rate,
                        water_liquid_capacity_water_temperature)
                    water_outlet_temperature_cache.param.append(water_temperature_derivative)

                    air_enthalpy_derivative = self.get_dha_dz(
                        air_capacity_air_temperature, air_humidity,
                        water_vapor_capacity_air_temperature,
                        air_temperature_derivative, air_inlet_temperature - 273.15,
                        humidity_derivative)
                    humid_air_enthalpy_cache.param.append(air_enthalpy_derivative)

                else:
                    diffusivity_constant = (merkel_number / (step)) * water_mass_flow_rate
                    air_capacity_air_temperature = self.get_c_pa(air_inlet_temperature)
                    water_vapor_capacity_water_temperature = self.get_c_pv(water_outlet_temperature)
                    water_vapor_capacity_air_temperature = self.get_c_pv(air_inlet_temperature)
                    water_liquid_capacity_water_temperature = self.get_c_w(water_outlet_temperature)
                    water_liquid_capacity_air_temperature = self.get_c_w(air_inlet_temperature)

                    vapor_pressure_water_temperature = self.get_p_wv(water_outlet_temperature)
                    saturation_humidity_ratio = self.get_w_ws(ambient_pressure, vapor_pressure_water_temperature)

                    vapor_pressure_air_temperature = self.get_p_wv(air_inlet_temperature)
                    saturation_humidity_air_temperature = self.get_w_ws(ambient_pressure, vapor_pressure_air_temperature)

                    lewis_number = self.get_Le(saturation_humidity_ratio, saturation_humidity_air_temperature)

                    water_mass_flow_rate_derivative = self.get_dmw_dz_sat(diffusivity_constant, saturation_humidity_ratio,
                                                                     saturation_humidity_air_temperature)
                    water_mass_flow_rate_cache.param.append(water_mass_flow_rate_derivative)

                    humidity_derivative = self.get_dX_dZ_sat(diffusivity_constant, saturation_humidity_ratio,
                                                        saturation_humidity_air_temperature, air_mass_flow_rate)
                    humidity_cache.param.append(humidity_derivative)

                    humidity_derivative_to_air_temperature = 0.0042 * 0.0609 * math.exp(
                        0.0609 * (air_inlet_temperature - 273))
                    air_temperature_derivative = self.get_dTa_dZ_sat(
                        diffusivity_constant, air_mass_flow_rate, lewis_number,
                        air_inlet_temperature - 273.15,
                        water_outlet_temperature - 273.15,
                        saturation_humidity_ratio, water_latent_heat,
                        water_vapor_capacity_water_temperature,
                        water_liquid_capacity_air_temperature, air_humidity,
                        saturation_humidity_air_temperature,
                        water_vapor_capacity_air_temperature,
                        air_capacity_air_temperature,
                        humidity_derivative_to_air_temperature)

                    air_inlet_temperature_cache.param.append(air_temperature_derivative)

                    water_temperature_derivative = self.get_dTw_dZ_sat(
                        diffusivity_constant, water_latent_heat,
                        water_vapor_capacity_water_temperature,
                        water_outlet_temperature - 273.15,
                        water_liquid_capacity_water_temperature,
                        saturation_humidity_ratio,
                        saturation_humidity_air_temperature, lewis_number,
                        air_inlet_temperature - 273.15,
                        air_capacity_air_temperature,
                        water_liquid_capacity_air_temperature, air_humidity,
                        water_vapor_capacity_air_temperature,
                        water_mass_flow_rate)
                    water_outlet_temperature_cache.param.append(water_temperature_derivative)

                    air_enthalpy_derivative = self.get_dha_dz_sat(
                        water_vapor_capacity_air_temperature,
                        air_inlet_temperature - 273.15,
                        water_liquid_capacity_air_temperature,
                        humidity_derivative_to_air_temperature,
                        saturation_humidity_air_temperature,
                        air_temperature_derivative, air_capacity_air_temperature,
                        air_humidity, humidity_derivative)

                    humid_air_enthalpy_cache.param.append(air_enthalpy_derivative)

                if j == 2:
                    water_outlet_temperature = water_outlet_temperature_cache.value + water_temperature_derivative
                    air_inlet_temperature = air_inlet_temperature_cache.value + air_temperature_derivative
                    air_humidity = humidity_cache.value + humidity_derivative
                    water_mass_flow_rate = water_mass_flow_rate_cache.value + water_mass_flow_rate_derivative
                    humid_air_enthalpy = humid_air_enthalpy_cache.value + air_enthalpy_derivative

                else:
                    water_outlet_temperature = water_outlet_temperature_cache.value + water_temperature_derivative / 2
                    air_inlet_temperature = air_inlet_temperature_cache.value + air_temperature_derivative / 2
                    air_humidity = humidity_cache.value + humidity_derivative / 2
                    water_mass_flow_rate = water_mass_flow_rate_cache.value + water_mass_flow_rate_derivative / 2
                    humid_air_enthalpy = humid_air_enthalpy_cache.value + air_enthalpy_derivative / 2

            water_temperature.append(water_outlet_temperature_cache.getNewValue())
            air_temperature.append(air_inlet_temperature_cache.getNewValue())
            humidity.append(humidity_cache.getNewValue())
            water_flow_rate.append(water_mass_flow_rate_cache.getNewValue())
            air_enthalpy.append(humid_air_enthalpy_cache.getNewValue())

            if station == False:
                vapor_pressure_water_temperature = self.get_p_wv(air_inlet_temperature)
                saturation_humidity_ratio = self.get_w_ws(ambient_pressure, vapor_pressure_water_temperature)
                relative_humidity = humidity[-1] / saturation_humidity_ratio * 100
                wet_bulb_temperature = self.getWetBulb(relative_humidity, air_temperature[-1] - 273.15)

                if wet_bulb_temperature > air_temperature[-1] - 273.15:
                    station = True

        return water_temperature[-1], water_flow_rate[-1], air_temperature[-1] - 273.15, humidity[-1]


    def forward(
            self,
            water_inlet_temperature,
            water_outlet_temperature,
            air_inlet_temperature,
            relative_humidity,
            water_mass_flow_rate,
            fan_rated_mass_flow_rate,
            fan_station,
            wind_velocity,
            ambient_pressure=101712.27
    ):
        air_humidity = HAPropsSI('W', 'T', air_inlet_temperature + 273.15, 'P', ambient_pressure, 'RH',
                                 relative_humidity)
        if fan_station:
            summary_error = inf

            air_mass_flow_rate_region = None
            water_mass_flow_rate_region = None

            water_mass_flow_rate_bottom = 1e-5
            water_mass_flow_rate_top = 20000
            water_mass_flow_rate_difference = ((water_mass_flow_rate_top - water_mass_flow_rate_bottom) / 2)

            air_mass_flow_rate_bottom = 1e-5
            air_mass_flow_rate_top = 20000
            air_mass_flow_rate_difference = ((air_mass_flow_rate_top - air_mass_flow_rate_bottom) / 2)

            solutions_water_mass_flow_rate = []
            solutions_air_mass_flow_rate = []
            merkels = []

            while True:
                water_inlet_mass_flow_rate = water_mass_flow_rate_bottom
                while water_inlet_mass_flow_rate <= water_mass_flow_rate_top:
                    air_inlet_mass_flow_rate = air_mass_flow_rate_bottom
                    while air_inlet_mass_flow_rate <= air_mass_flow_rate_top:
                        try:
                            merkel_number = self.get_merkel_number(
                                water_inlet_temperature,
                                water_outlet_temperature,
                                air_inlet_temperature,
                                air_humidity,
                                water_mass_flow_rate,
                                air_inlet_mass_flow_rate,
                                ambient_pressure)
                            water_temperature, water_flow, air_outlet_temperature, humidity = (
                                self.heat_exchanger_cooling_tower(
                                    merkel_number,
                                    water_outlet_temperature,
                                    air_inlet_temperature,
                                    water_inlet_mass_flow_rate,
                                    air_inlet_mass_flow_rate,
                                    air_humidity,
                                    ambient_pressure))
                            actual_flow_difference = (abs(water_flow - water_mass_flow_rate) / water_mass_flow_rate) * 100
                            actual_temperature_difference = (abs((water_temperature - 273.15) - water_inlet_temperature) /
                                                             water_inlet_temperature * 100)

                            actual_error = actual_flow_difference + actual_temperature_difference

                            if actual_error < summary_error:
                                water_mass_flow_rate_region = water_inlet_mass_flow_rate
                                air_mass_flow_rate_region = air_inlet_mass_flow_rate
                                merkels.append(merkel_number)
                                summary_error = actual_error
                        except:
                            pass

                        air_inlet_mass_flow_rate += air_mass_flow_rate_difference
                    water_inlet_mass_flow_rate += water_mass_flow_rate_difference

                solutions_water_mass_flow_rate.append(water_mass_flow_rate_region)
                solutions_air_mass_flow_rate.append(air_mass_flow_rate_region)

                # if m_w_REG != m_w_BOTTOM:
                water_mass_flow_rate_bottom = water_mass_flow_rate_region - (water_mass_flow_rate_difference / 2)
                # if m_w_REG != m_w_TOP:
                water_mass_flow_rate_top = water_mass_flow_rate_region + (water_mass_flow_rate_difference / 2)
                water_mass_flow_rate_difference = (water_mass_flow_rate_top - water_mass_flow_rate_bottom) / 2

                if air_mass_flow_rate_region != air_mass_flow_rate_bottom:
                    air_mass_flow_rate_bottom = air_mass_flow_rate_region - (air_mass_flow_rate_difference / 2)
                if air_mass_flow_rate_region != air_mass_flow_rate_top:
                    air_mass_flow_rate_top = air_mass_flow_rate_region + (air_mass_flow_rate_difference / 2)
                air_mass_flow_rate_difference = (air_mass_flow_rate_top - air_mass_flow_rate_bottom) / 2

                if water_mass_flow_rate_difference < 0.01 and air_mass_flow_rate_difference < 0.01:
                    break

            summary_error = inf
            water_inlet_mass_flow_rate = solutions_water_mass_flow_rate[-1]
            solutions_air_mass_flow_rate = []

            air_mass_flow_rate_bottom = 1e-5
            air_mass_flow_rate_top = 20000
            air_mass_flow_rate_difference = ((air_mass_flow_rate_top - air_mass_flow_rate_bottom) / 2)

            while True:
                air_inlet_mass_flow_rate = air_mass_flow_rate_bottom
                while air_inlet_mass_flow_rate <= air_mass_flow_rate_top:
                    try:
                        merkel_number = self.get_merkel_number(
                            water_inlet_temperature, water_outlet_temperature,
                            air_inlet_temperature, air_humidity, water_mass_flow_rate,
                            air_inlet_mass_flow_rate,
                            ambient_pressure)
                        water_temperature, water_flow, air_outlet_temperature, humidity = (
                            self.heat_exchanger_cooling_tower(
                                merkel_number, water_outlet_temperature, air_inlet_temperature,
                                water_inlet_mass_flow_rate, air_inlet_mass_flow_rate, air_humidity,
                                ambient_pressure))
                        waterOutCalc = water_mass_flow_rate - air_inlet_mass_flow_rate * (humidity - air_humidity)
                        waterError = (abs(water_inlet_mass_flow_rate - waterOutCalc) / water_inlet_mass_flow_rate) * 100
                        actual_flow_difference = ((abs(water_flow - water_mass_flow_rate)) / water_mass_flow_rate) * 100
                        actual_temperature_difference = ((abs((water_temperature - 273.15) - water_inlet_temperature)) /
                                                         water_inlet_temperature) * 100

                        actual_error = actual_temperature_difference + actual_flow_difference + waterError
                        if actual_error < summary_error:
                            air_mass_flow_rate_region = air_inlet_mass_flow_rate
                            summary_error = actual_error
                            solutions_air_mass_flow_rate.append(air_mass_flow_rate_region)
                    except:
                        pass
                    air_inlet_mass_flow_rate += air_mass_flow_rate_difference / 20

                if air_mass_flow_rate_region != air_mass_flow_rate_bottom:
                    air_mass_flow_rate_bottom = air_mass_flow_rate_region - (air_mass_flow_rate_difference / 2)
                if air_mass_flow_rate_region != air_mass_flow_rate_top:
                    air_mass_flow_rate_top = air_mass_flow_rate_region + (air_mass_flow_rate_difference / 2)

                air_mass_flow_rate_difference = (air_mass_flow_rate_top - air_mass_flow_rate_bottom) / 2

                if air_mass_flow_rate_difference < 0.1:
                    air_inlet_mass_flow_rate = air_mass_flow_rate_region
                    break
        else:
            merkel_number = 1.625
            air_inlet_mass_flow_rate = wind_velocity*2*1.225


        water_outlet_temperature, water_outlet_flow_rate, air_outlet_temperature, outlet_humidity = (
            self.heat_exchanger_cooling_tower(
                merkel_number, water_outlet_temperature, air_inlet_temperature,
                water_mass_flow_rate, air_inlet_mass_flow_rate, air_humidity,
                ambient_pressure))
        return (water_outlet_temperature, air_outlet_temperature, outlet_humidity, air_mass_flow_rate_region,
                water_mass_flow_rate_region)


if __name__ == '__main__':

    cooling_tower_model = CoolingTowerModel()

    water_outlet_temperature = 31
    water_inlet_temperature = 36
    air_inlet_temperature = 30
    ambient_pressure = 101712
    relative_humidity = HAPropsSI('R', 'T', air_inlet_temperature + 273.15, 'W', 0.008127, 'P', ambient_pressure)
    wet_bulb_temperature = HAPropsSI('B', 'T',  air_inlet_temperature + 273.15,
                                     'RH', relative_humidity, 'P', ambient_pressure)-273.15
    water_mass_flow_rate = 2000

    (water_outlet_temperature, air_outlet_temperature, outlet_humidity, air_mass_flow_rate_region,
     water_mass_flow_rate_region) = cooling_tower_model.forward(
        water_inlet_temperature=water_inlet_temperature,
        water_outlet_temperature=water_outlet_temperature,
        air_inlet_temperature=air_inlet_temperature,
        relative_humidity=relative_humidity,
        water_mass_flow_rate=water_mass_flow_rate,
        fan_rated_mass_flow_rate=1000,
        fan_station=True,
        wind_velocity=0,
        ambient_pressure=ambient_pressure)

    print(f"air outlet temperature is {air_outlet_temperature}, "
          f"air flow rate is {air_mass_flow_rate_region},"
          f"water outlet flow rate is {water_mass_flow_rate_region}, "
          f"humidity is {outlet_humidity}")