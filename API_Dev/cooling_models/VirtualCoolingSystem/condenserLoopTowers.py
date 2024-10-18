from loguru import logger
from CoolProp.CoolProp import PropsSI
from dotmap import DotMap
import pandas as pd
import matplotlib.pyplot as plt


def SolveRoot(
        Eps,  # required absolute accuracy
        MaxIte,  # maximum number of allowed iterations
        Flag,  # integer storing exit status
        XRes,  # value of x that solves f(x,Par) = 0
        f,  # function
        X_0,  # 1st bound of interval that contains the solution
        X_1  # 2nd bound of interval that contains the solution
    ):
    """
    PURPOSE OF THIS SUBROUTINE:
        Find the value of x between x0 and x1 such that f(x,Par) is equal to zero.
    METHODOLOGY EMPLOYED:
        Uses the Regula Falsi (false position) method (similar to secant method) SUBROUTINE ARGUMENT DEFINITIONS:
            = -2: f(x0) and f(x1) have the same sign
            = -1: no convergence
            >  0: number of iterations performed
    """
    SMALL = 1e-10
    X0 = X_0  # present 1st bound
    X1 = X_1  # present 2nd bound
    XTemp = X0  # new estimate
    NIte = 0  # number of iterations
    AltIte = 0  # a counter used for Alternation choice
    Y0 = f(X0)  # f at X0
    Y1 = f(X1)  # f at X1

    if Y0 * Y1 > 0:
        Flag = -2
        XRes = X0
        return Flag, XRes

    while True:
        DY = Y0 - Y1

        if abs(DY) < SMALL:
            DY = SMALL

        if abs(X1 - X0) < SMALL:
            break

        XTemp = (Y0 * X1 - Y1 * X0) / DY
        YTemp = f(XTemp)

        NIte += 1
        AltIte += 1

        if abs(YTemp) < Eps:
            Flag = NIte
            XRes = XTemp
            return Flag, XRes

        # OK, so we didn't converge, lets check max iterations to see if we should break early
        if NIte > MaxIte:
            break

        # Finally, if we make it here, we have not converged, and we still have iterations left, so continue
        # and reassign values (only if further iteration required)

        if Y0 < 0.0:
            if YTemp < 0.0:
                X0 = XTemp
                Y0 = YTemp
            else:
                X1 = XTemp
                Y1 = YTemp
        else:
            if YTemp < 0.0:
                X1 = XTemp
                Y1 = YTemp
            else:
                X0 = XTemp
                Y0 = YTemp

    # if we make it here we haven't converged, so just set the flag and leave
    Flag = -1
    XRes = XTemp
    return Flag, XRes


class CalculateVariableSpeedTower:
    def __init__(self, config):
        self.config = config
        self.SingleSetPoint = True
        self.TempSetPoint = 30

        self.MinInletAirWBTemp = -34.4
        self.MaxInletAirWBTemp = 29.4444
        self.MinRangeTemp = 1.1111
        self.MaxRangeTemp = 22.2222
        self.MinApproachTemp = 1.1111
        self.MaxApproachTemp = 40.0
        self.MinWaterFlowRatio = 0.75
        self.MaxWaterFlowRatio = 1.25
        self.MaxLiquidToGasRatio = 8.0

        self.MaxIte = 500
        self.Acc = 0.0001
        self.SolFla = True
        self.constant_pointfive = 0.5
        self.HighSpeedFanPower = self.config.designFanPower
        self.FanPowerfAirFlowCurve = True

        # YorkCalc coefficients
        self.YorCalcCoe = [-0.359741205,
                           -0.055053608,
                           0.0023850432,
                           0.173926877,
                           -0.0248473764,
                           0.00048430224,
                           -0.005589849456,
                           0.0005770079712,
                           -0.00001342427256,
                           2.84765801111111,
                           -0.121765149,
                           0.0014599242,
                           1.680428651,
                           -0.0166920786,
                           -0.0007190532,
                           -0.025485194448,
                           0.0000487491696,
                           0.00002719234152,
                           -0.0653766255555556,
                           -0.002278167,
                           0.0002500254,
                           -0.0910565458,
                           0.00318176316,
                           0.000038621772,
                           -0.0034285382352,
                           0.00000856589904,
                           -0.000001516821552]

        self.FanPowerCoe = [-9.315163e-03,
                            0.0512333965844443,
                            -8.383647e-02,
                            1.04191823356909]

        self._calibrate_flow()

    def _calibrate_flow(self):
        """calibrate variable speed tower model based on user input by finding calibration water flow rate ratio that
           yields an approach temperature that matches user input"""

        # check range for water flow rate ratio (make sure RegulaFalsi converges)
        MaxWaterFlowRateRatio = 0.5  # maximum water flow rate ratio which yields desired approach temp
        Tapproach = 0.0  # temporary tower approach temp variable [C]

        FlowRateRatioStep = (self.MaxWaterFlowRatio - self.MinWaterFlowRatio) / 10
        ModelCalibrated = True

        ModelWaterFlowRatioMax = self.MaxWaterFlowRatio * 4  # maximum water flow rate ratio used for model calibration

        # find a flow rate large enough to provide an approach temperature > than the user defined approach
        # WaterFlowRateRatio: tower water flow rate ratio
        WaterFlowRateRatio = 0.0
        while Tapproach < self.config.designApproachTemperature and MaxWaterFlowRateRatio <= ModelWaterFlowRatioMax:
            WaterFlowRateRatio = MaxWaterFlowRateRatio
            Tapproach = self.calculateVariableSpeedApproach(WaterFlowRateRatio,
                                                            1.01,
                                                            self.config.designInletAirWetBulbTemperature,
                                                            self.config.designRangeTemperature)
            if Tapproach < self.config.designApproachTemperature:
                MaxWaterFlowRateRatio += FlowRateRatioStep

            # water flow rate large enough to provide an approach temperature > than the user defined approach does not
            # exist within the tolerances specified by the user
            if ((MaxWaterFlowRateRatio == 0.5 and Tapproach < self.config.designApproachTemperature) or
                    (MaxWaterFlowRateRatio >= ModelWaterFlowRatioMax)):
                ModelCalibrated = False
                break

        WaterFlowRatio = 0.0  # tower water flow rate ratio found during model calibration

        if ModelCalibrated:
            def f_calib(FlowRatio):
                Tact = self.calculateVariableSpeedApproach(FlowRatio,
                                                           1.01,
                                                           self.config.designInletAirWetBulbTemperature,
                                                           self.config.designRangeTemperature)
                return self.config.designApproachTemperature - Tact

            SolFla, WaterFlowRatio = SolveRoot(self.Acc, self.MaxIte, self.SolFla, WaterFlowRatio, f_calib,
                                               self.constant_pointfive,
                                               MaxWaterFlowRateRatio)

            if SolFla == -1:
                logger.error("Iteration limit exceeded in calculating tower water flow ratio during calibration")
                logger.error("Inlet air wet-bulb, range, and/or approach temperature does not allow calibration of "
                             "water flow rate ratio for this variable-speed cooling tower")
                logger.error("Cooling tower calibration failed for the tower")
            elif SolFla == -2:
                logger.error("Bad starting values for cooling tower water flow rate ratio calibration")
                logger.error("Inlet air wet-bulb, range, and/or approach temperature does not allow calibration of "
                             "water flow rate ratio for this variable-speed cooling tower")
                logger.error("Cooling tower calibration failed for the tower")
        else:
            logger.error("Bad starting values for cooling tower water flow rate ratio calibration")
            logger.error("Design inlet air wet-bulb or range temperature must be modified to achieve the design "
                         "approach")
            logger.error(f"A water flow rate ratio of {WaterFlowRateRatio} was calculated to yield an approach "
                         f"temperature of {Tapproach}")
            logger.error("Cooling tower calibration failed for tower")

        self.CalibratedWaterFlowRate = self.config.designWaterFlowRate / WaterFlowRatio

        if WaterFlowRatio < self.MinWaterFlowRatio or WaterFlowRatio > self.MaxWaterFlowRatio:
            logger.warning(f"CoolingTower:VariableSpeed, the calibrated water flow rate ratio is determined to be "
                           f"{WaterFlowRatio:.5}. This is outside the valid range of {self.MinWaterFlowRatio:.5} to "
                           f"{self.MaxWaterFlowRatio:.5}")

        rho = self.get_fluid_property(fluid_name="water",
                                      temperature=self.config.designInletAirWetBulbTemperature +
                                                  self.config.designApproachTemperature +
                                                  self.config.designRangeTemperature,
                                      property_type="density")

        Cp = self.get_fluid_property(fluid_name="water",
                                     temperature=self.config.designInletAirWetBulbTemperature +
                                                 self.config.designApproachTemperature +
                                                 self.config.designRangeTemperature,
                                     property_type="specific_heat")

        self.TowerNominalCapacity = ((rho * self.config.designWaterFlowRate) * Cp * self.config.designRangeTemperature)
        logger.info(f"Tower Nominal Capacity: {self.TowerNominalCapacity:.5} [W]")

        self.FreeConvAirFlowRate = self.config.minimumAirFlowRateRatio * self.config.designAirFlowRate
        logger.info(f"Air Flow Rate in free convection regime {self.FreeConvAirFlowRate:.5f} [m3/s].")

        self.TowerFreeConvNomCap = self.TowerNominalCapacity * self.config.fractionOfTowerCapacityInFreeConvectionRegime
        logger.info(f"Tower capacity in free convection regime at design conditions {self.TowerFreeConvNomCap:.5f} [W]")

    def calculateVariableSpeedApproach(self,
                                       PctWaterFlow,  # Water flow ratio of cooling tower
                                       airFlowRatioLocal,  # Air flow ratio of cooling tower
                                       Twb,  # Inlet air wet-bulb temperature [C]
                                       Tr  # Cooling tower range (outlet water temp minus inlet air wet-bulb temp) [C]
                                       ):
        """ Calculate tower approach temperature (e.g. outlet water temp minus inlet air wet-bulb temp)
        given air flow ratio, water flow ratio, inlet air wet-bulb temp, and tower range.

        METHODOLOGY EMPLOYED:
            Calculation method used empirical models from CoolTools or York to determine performance
            of variable speed (variable air flow rate) cooling towers.
        """

        PctAirFlow = airFlowRatioLocal
        FlowFactor = PctWaterFlow / PctAirFlow

        return self.YorCalcCoe[0] + self.YorCalcCoe[1] * Twb + self.YorCalcCoe[2] * Twb * Twb + self.YorCalcCoe[3] * Tr + \
            self.YorCalcCoe[4] * Twb * Tr + self.YorCalcCoe[5] * Twb * Twb * Tr + self.YorCalcCoe[6] * Tr * Tr + \
            self.YorCalcCoe[7] * Twb * Tr * Tr + self.YorCalcCoe[8] * Twb * Twb * Tr * Tr + self.YorCalcCoe[9] * \
            FlowFactor + self.YorCalcCoe[10] * Twb * FlowFactor + self.YorCalcCoe[11] * Twb * Twb * FlowFactor + \
            self.YorCalcCoe[12] * Tr * FlowFactor + self.YorCalcCoe[13] * Twb * Tr * FlowFactor + self.YorCalcCoe[14] * \
            Twb * Twb * Tr * FlowFactor + self.YorCalcCoe[15] * Tr * Tr * FlowFactor + self.YorCalcCoe[16] * Twb * Tr * \
            Tr * FlowFactor + self.YorCalcCoe[17] * Twb * Twb * Tr * Tr * FlowFactor + self.YorCalcCoe[18] * FlowFactor * \
            FlowFactor + self.YorCalcCoe[19] * Twb * FlowFactor * FlowFactor + self.YorCalcCoe[20] * Twb * Twb * \
            FlowFactor * FlowFactor + self.YorCalcCoe[21] * Tr * FlowFactor * FlowFactor + self.YorCalcCoe[22] * Twb * \
            Tr * FlowFactor * FlowFactor + self.YorCalcCoe[23] * Twb * Twb * Tr * FlowFactor * FlowFactor + \
            self.YorCalcCoe[24] * Tr * Tr * FlowFactor * FlowFactor + self.YorCalcCoe[25] * Twb * Tr * Tr * FlowFactor * \
            FlowFactor + self.YorCalcCoe[26] * Twb * Twb * Tr * Tr * FlowFactor * FlowFactor

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

    def checkModelBounds(self,
                         Twb,  # current inlet air wet-bulb temperature (C)
                         Tr,  # requested range temperature for current time step (C)
                         Ta,  # requested approach temperature for current time step (C)
                         WaterFlowRateRatio,  # current water flow rate ratio at water inlet node
                         TwbCapped,  # bounded value of inlet air wet-bulb temperature (C)
                         TrCapped,  # bounded value of range temperature (C)
                         TaCapped,  # bounded value of approach temperature (C)
                         WaterFlowRateRatioCapped  # bounded value of water flow rate ratio
                         ):
        """
        To verify that the empirical model's independent variables are within the limits used during the
        development of the empirical model.

        METHODOLOGY EMPLOYED:
            The empirical models used for simulating a variable speed cooling tower are based on a limited data set.
            Extrapolation of empirical models can cause instability and the independent variables may need to be
            limited. The range of each independent variable is provided either by the CoolTools or York model limits, or
            specified by the user if the model is User Defined (in either the CoolTools or York model format).
            These limits are tested in this subroutine each time step and returned for use by the calling routine.
            The independent variables capped here may or may not be passed to the empirical model in the calling
            routine depending on their use.
        """

        # initialize capped variables in case independent variables are in bounds
        TwbCapped = Twb
        TrCapped = Tr
        TaCapped = Ta
        WaterFlowRateRatioCapped = WaterFlowRateRatio

        """
        Print warning messages only when valid and only for the first occurrence. Let summary provide statistics.
        Wait for next time step to print warnings. If simulation iterates, print out
        the warning for the last iteration only. Must wait for next time step to accomplish this.
        If a warning occurs and the simulation down shifts, the warning is not valid.
        """

        if Twb < self.MinInletAirWBTemp:
            TwbCapped = self.MinInletAirWBTemp

        if Twb > self.MaxInletAirWBTemp:
            TwbCapped = self.MaxInletAirWBTemp

        if Tr < self.MinRangeTemp:
            TrCapped = self.MinRangeTemp

        if Tr > self.MaxRangeTemp:
            TrCapped = self.MaxRangeTemp

        if Ta < self.MinApproachTemp:
            TaCapped = self.MinApproachTemp

        if Ta > self.MaxApproachTemp:
            TaCapped = self.MaxApproachTemp

        if WaterFlowRateRatio < self.MinWaterFlowRatio:
            WaterFlowRateRatioCapped = self.MinWaterFlowRatio

        if WaterFlowRateRatio > self.MaxWaterFlowRatio:
            WaterFlowRateRatioCapped = self.MaxWaterFlowRatio

        return TwbCapped, TrCapped, TaCapped, WaterFlowRateRatioCapped

    def calculateVariableTowerOutletTemp(self,
                                         WaterFlowRateRatio,  # current water flow rate ratio (capped if applicable)
                                         airFlowRateRatioLocal,  # current air flow rate ratio
                                         Twb,  # current inlet air wet-bulb temperature (C, capped if applicable)
                                         Node_inlet_temp  # cooling tower inlet water temperature
                                         ):
        """
        PURPOSE OF THIS SUBROUTINE:
            To calculate the leaving water temperature of the variable speed cooling tower.

        METHODOLOGY EMPLOYED:
            The range temperature is varied to determine balance point where model output (Tapproach),
            range temperature and inlet air wet-bulb temperature show a balance as:
            Twb + Tapproach + Trange = Node(WaterInletNode)%Temp
        """

        MaxIte = 500  # Maximum number of iterations
        Acc = 0.0001  # Accuracy of result

        # SUBROUTINE LOCAL VARIABLE DECLARATIONS:
        VSTowerMaxRangeTemp = 22.222  # set VS cooling tower range maximum value used for solver

        # determine tower outlet water temperature
        Tr = None  # range temperature which results in an energy balance

        def f(Trange):
            Tapproach = self.calculateVariableSpeedApproach(WaterFlowRateRatio, airFlowRateRatioLocal, Twb, Trange)
            # Calculate the residual based on the balance equation
            return (Twb + Tapproach + Trange) - Node_inlet_temp

        SolFla = 0
        SolFla, Tr = SolveRoot(Acc, MaxIte, SolFla, Tr, f, 0.001, VSTowerMaxRangeTemp)
        WaterTemp = Node_inlet_temp
        OutletWaterTempLocal = WaterTemp - Tr

        if SolFla == -1:
            logger.error("Iteration limit exceeded in calculating tower nominal capacity at minimum air flow ratio. "
                         "Design inlet air wet-bulb or approach temperature must be modified to achieve an acceptable "
                         "range at the minimum air flow rate. Cooling tower simulation failed to converge for tower.")
        # if SolFla = -2, Tr is returned as minimum value (0.001) and outlet temp = inlet temp - 0.001
        elif SolFla == -2:  # decide if should run at max flow
            # Determine temperature setpoint based on the calculation scheme
            if self.SingleSetPoint:
                TempSetPoint = self.TempSetPoint # local temporary for loop set point
            else:
                raise Exception("Unknown LoopDemandCalcScheme")  # Raise an error if scheme is unknown

            # Check if the system should operate at maximum cooling tower flow
            if WaterTemp > (TempSetPoint + self.MaxRangeTemp):
                # Run the tower at full capacity (flat out)
                OutletWaterTempLocal = WaterTemp - self.MaxRangeTemp

        return OutletWaterTempLocal  # Return the calculated outlet water temperature

    def fanPowerOfAirFlowCurve(self, airFlowRateRatio):
        return (self.FanPowerCoe[0] + self.FanPowerCoe[1] * airFlowRateRatio + self.FanPowerCoe[2] *
                airFlowRateRatio ** 2 + self.FanPowerCoe[3] * airFlowRateRatio ** 3)

    def run(self, WaterMassFlowRate=1.0, Node_WaterInletNodeTemp=32, AirWetBulb=26.6, TempSetPoint=30):

        """
        PURPOSE OF THIS SUBROUTINE:
            To simulate the operation of a variable-speed fan cooling tower.

        METHODOLOGY EMPLOYED:
        For each simulation time step, a desired range temperature (Twater,inlet-Twater,setpoint) and desired approach
        temperature (Twater,setpoint-Tair,WB) is calculated which meets the outlet water temperature setpoint. This
        desired range and approach temperature also provides a balance point for the empirical model where:
        air,WB + Twater,range + Tapproach = Node(WaterInletNode)%Temp
        Calculation of water outlet temperature uses one of the following equations:
        Twater,outlet = Tair,WB + Tapproach          (1)  or
        Twater,outlet = Twater,inlet - Twater,range  (2)
        If a solution (or balance) is found, these 2 calculation methods are equal. Equation 2 is used to calculate
        the outlet water temperature in the free convection regime and at the minimum or maximum fan speed so that
        if a solution is not reached, the outlet water temperature is approximately equal to the inlet water temperature
        and the tower fan must be varied to meet the setpoint. Equation 1 is used when the fan speed is varied between
        the minimum and maximum fan speed to meet the outlet water temperature setpoint.
        The outlet water temperature in the free convection regime is first calculated to see if the setpoint is met.
        If the setpoint is met, the fan is OFF and the outlet water temperature is allowed to float below the set
        point temperature. If the setpoint is not met, the outlet water temperature is re-calculated at the minimum
        fan speed. If the setpoint is met, the fan is cycled to exactly meet the outlet water temperature setpoint.
        If the setpoint is not met at the minimum fan speed, the outlet water temperature is re-calculated at the
        maximum fan speed. If the setpoint at the maximum fan speed is not met, the fan runs at maximum speed the
        entire time step. If the setpoint is met at the maximum fan speed, the fan speed is varied to meet the setpoint.
        If a tower has multiple cells, the specified inputs of or the autosized capacity
        and air/water flow rates are for the entire tower. The number of cells to operate
        is first determined based on the user entered minimal and maximal water flow fractions
        per cell. If the loads are not met, more cells (if available) will operate to meet
        the loads. Inside each cell, the fan speed varies in the same way.
        """

        self.TempSetPoint = TempSetPoint

        WaterMassFlowRatePerCellMin = 0.0
        NumCellMin = 0
        NumCellMax = 0

        InitConvTemp = 5.05
        rho = self.get_fluid_property(fluid_name="water",
                                      temperature=InitConvTemp,
                                      property_type="density")

        DesWaterMassFlowRate = self.config.designWaterFlowRate * rho

        if DesWaterMassFlowRate > 0.0:
            WaterMassFlowRatePerCellMin = (DesWaterMassFlowRate * self.config.cellMinimumWaterFlowRateFraction /
                                           self.config.numberOfCells)
            WaterMassFlowRatePerCellMax = (DesWaterMassFlowRate * self.config.cellMaximumWaterFlowRateFraction /
                                           self.config.numberOfCells)

            # round it up to the nearest integer
            NumCellMin = min(int((WaterMassFlowRate / WaterMassFlowRatePerCellMax) + 0.999), self.config.numberOfCells)
            NumCellMax = min(int((WaterMassFlowRate / WaterMassFlowRatePerCellMin) + 0.999), self.config.numberOfCells)

        if NumCellMin <= 0:
            NumCellMin = 1
        if NumCellMax <= 0:
            NumCellMax = 1

        if self.config.cellControl == "MinimalCell":
            NumCellOn = NumCellMin
        else:
            NumCellOn = NumCellMax

        WaterMassFlowRatePerCell = WaterMassFlowRate / NumCellOn

        # Initialize subroutine variables
        FanPower = 0.0
        OutletWaterTemp = Node_WaterInletNodeTemp
        Twb = AirWetBulb
        TwbCapped = AirWetBulb

        # water temperature set point
        TempSetPoint = 0.0  # Outlet water temperature set point (C)
        if self.SingleSetPoint:
            TempSetPoint = self.TempSetPoint

        Tr = Node_WaterInletNodeTemp - TempSetPoint
        Ta = TempSetPoint - AirWetBulb

        # loop to increment NumCell if we cannot meet the set point with the actual number of cells calculated above
        IncrNumCellFlag = True
        OutletWaterTempOFF = None  # Outlet water temperature with fan OFF (C)
        OutletWaterTempON = 0.0  # Outlet water temperature with fan ON at maximum fan speed (C)
        FreeConvectionCapFrac = 0.0  # Fraction of tower capacity in free convection

        WaterFlowRateRatioCapped = 0.0  # Water flow rate ratio passed to VS tower model
        TrCapped = None  # range temp passed to VS tower model
        TaCapped = None  # approach temp passed to VS tower model

        FanCyclingRatio = 1.0
        airFlowRateRatio = 1.0

        while IncrNumCellFlag:
            IncrNumCellFlag = False
            WaterDensity = self.get_fluid_property(fluid_name="water",
                                                   temperature=Node_WaterInletNodeTemp,
                                                   property_type="density")

            WaterFlowRateRatio = WaterMassFlowRatePerCell / (WaterDensity * self.CalibratedWaterFlowRate /
                                                             self.config.numberOfCells)

            # check independent inputs with respect to model boundaries
            TwbCapped, TrCapped, TaCapped, WaterFlowRateRatioCapped = self.checkModelBounds(Twb, Tr, Ta,
                                                                                            WaterFlowRateRatio,
                                                                                            TwbCapped, TrCapped,
                                                                                            TaCapped,
                                                                                            WaterFlowRateRatioCapped)

            """
            determine the free convection capacity by finding the outlet temperature at full air flow and multiplying
            the tower's full capacity temperature difference by the percentage of tower capacity in free convection
            regime specified by the user
            """

            airFlowRateRatio = 1.0
            OutletWaterTempOFF = Node_WaterInletNodeTemp
            OutletWaterTemp = OutletWaterTempOFF
            FreeConvectionCapFrac = self.config.fractionOfTowerCapacityInFreeConvectionRegime
            OutletWaterTempON = self.calculateVariableTowerOutletTemp(WaterFlowRateRatioCapped, airFlowRateRatio,
                                                                      TwbCapped, Node_WaterInletNodeTemp)

            if OutletWaterTempON > TempSetPoint:
                FanCyclingRatio = 1.0
                airFlowRateRatio = 1.0
                FanPower = self.HighSpeedFanPower * NumCellOn / self.config.numberOfCells
                OutletWaterTemp = OutletWaterTempON
                if (NumCellOn < self.config.numberOfCells and WaterMassFlowRate / (NumCellOn + 1) >
                        WaterMassFlowRatePerCellMin):
                    NumCellOn += 1
                    WaterMassFlowRatePerCell = WaterMassFlowRate / NumCellOn
                    IncrNumCellFlag = True

        # find the correct air ratio only if full flow is  too much
        if OutletWaterTempON < TempSetPoint:
            # outlet water temperature is calculated in the free convection regime
            OutletWaterTempOFF = Node_WaterInletNodeTemp - FreeConvectionCapFrac * (Node_WaterInletNodeTemp -
                                                                                    OutletWaterTempON)
            # fan is OFF
            FanCyclingRatio = 0.0

            # air flow ratio is assumed to be the fraction of tower capacity in the free convection regime
            # (fan is OFF but air is flowing)
            airFlowRateRatio = FreeConvectionCapFrac

            # Assume set point was met using free convection regime (pump ON and fan OFF)
            FanPower = 0.0
            OutletWaterTemp = OutletWaterTempOFF

            if OutletWaterTempOFF > TempSetPoint:
                # Set point was not met, turn on cooling tower fan at minimum fan speed
                airFlowRateRatio = self.config.minimumAirFlowRateRatio

                # Outlet water temperature with fan at minimum speed (C)
                OutletWaterTempMIN = self.calculateVariableTowerOutletTemp(WaterFlowRateRatioCapped,
                                                                           airFlowRateRatio,
                                                                           TwbCapped,
                                                                           Node_WaterInletNodeTemp)
                if OutletWaterTempMIN < TempSetPoint:
                    # if set point was exceeded, cycle the fan at minimum air flow to meet the set point temperature
                    if self.FanPowerfAirFlowCurve == 0:
                        FanPower = (airFlowRateRatio ** 3 * self.HighSpeedFanPower * NumCellOn /
                                    self.config.numberOfCells)
                    else:
                        FanCurveValue = self.fanPowerOfAirFlowCurve(airFlowRateRatio)
                        FanPower = max(0.0,
                                       (self.HighSpeedFanPower * FanCurveValue)) * NumCellOn / self.config.numberOfCells

                    # fan is cycling ON and OFF at the minimum fan speed. Adjust fan power and air flow rate ratio
                    # according to cycling rate
                    FanCyclingRatio = ((OutletWaterTempOFF - TempSetPoint) / (OutletWaterTempOFF - OutletWaterTempMIN))
                    FanPower *= FanCyclingRatio
                    OutletWaterTemp = TempSetPoint
                    airFlowRateRatio = ((FanCyclingRatio * self.config.minimumAirFlowRateRatio) +
                                        ((1 - FanCyclingRatio) * FreeConvectionCapFrac))
                else:
                    # if the set point was not met at minimum fan speed, set fan speed to maximum
                    airFlowRateRatio = 1.0
                    # fan will not cycle and runs the entire time step
                    FanCyclingRatio = 1.0

                    # Set point was met with pump ON and fan ON at full flow. Calculate the fraction of full air flow
                    # to exactly meet the set point temperature
                    def f(FlowRatio):
                        TapproachActual = self.calculateVariableSpeedApproach(WaterFlowRateRatioCapped, FlowRatio,
                                                                              TwbCapped, Tr)
                        return Ta - TapproachActual

                    SolFla = 0
                    SolFla, airFlowRateRatio = SolveRoot(self.Acc, self.MaxIte, SolFla, airFlowRateRatio, f,
                                                         self.config.minimumAirFlowRateRatio, 1.0)
                    if SolFla == -1:
                        logger.error("Cooling tower iteration limit exceeded when calculating air flow rate ratio for "
                                     "tower")
                    elif SolFla == -2:
                        logger.error("CoolingTower:VariableSpeed Cooling tower air flow rate ratio calculation failed")

                    # Use theoretical cubic for determination of fan power if user has not specified
                    # a fan power ratio curve

                    if self.FanPowerfAirFlowCurve == 0:
                        FanPower = (airFlowRateRatio ** 3 * self.HighSpeedFanPower * NumCellOn /
                                    self.config.numberOfCells)
                    else:
                        FanCurveValue = self.fanPowerOfAirFlowCurve(airFlowRateRatio)
                        FanPower = max(0.0,
                                       (self.HighSpeedFanPower * FanCurveValue)) * NumCellOn / self.config.numberOfCells
                    # outlet water temperature is calculated as the inlet air wet-bulb temperature plus
                    # tower approach temperature
                    OutletWaterTemp = Twb + Ta

        CpWater = self.get_fluid_property(fluid_name="water",
                                          temperature=Node_WaterInletNodeTemp,
                                          property_type="density")

        Qactual = WaterMassFlowRate * CpWater * (Node_WaterInletNodeTemp - OutletWaterTemp)

        error = abs(OutletWaterTemp-TempSetPoint)
        if error > 0.2:
            logger.warning(f"The set point temperature cannot be reached. Error: {error:.2f}")

        return DotMap(dict(TowerFanPower=FanPower, TowerQactual=Qactual, TowerOutletWaterTemp=OutletWaterTemp,
                           TowerFanCyclingRatio=FanCyclingRatio, TowerAirFlowRateRatio=airFlowRateRatio))


if __name__ == "__main__":

    config_spec = DotMap({
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

    tower = CalculateVariableSpeedTower(config_spec)

    results = tower.run(WaterMassFlowRate=4,
                        Node_WaterInletNodeTemp=32,
                        AirWetBulb=24.4,
                        TempSetPoint=30)

    print(results)


