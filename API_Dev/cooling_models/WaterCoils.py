# import time
#
# from loguru import logger
# from CoolProp.CoolProp import PropsSI
# from dotmap import DotMap
#
#
# """
# PURPOSE OF THIS MODULE:
#     To encapsulate the data and algorithms required to
#     manage the WaterCoil System Component
# """
#
#
# class Psychometric:
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def PsyCpAirFnW(dw):
#         """
#         humidity ratio {kgWater/kgDryAir}
#         PURPOSE OF THIS FUNCTION:
#             This function provides the heat capacity of air {J/kg-C} as function of humidity ratio.
#
#         METHODOLOGY EMPLOYED:
#             take numerical derivative of PsyHFnTdbW function
#
#         REFERENCES:
#             see PsyHFnTdbW ref. to ASHRAE Fundamentals
#             USAGE:  cpa = PsyCpAirFnW(w)
#         """
#
#         # compute heat capacity of air
#         w = max(dw, 1.0e-5)
#         return 1.00484e3 + w * 1.85895e3  # result => heat capacity of moist air {J/kg-C}
#
#
# class WaterCoils:
#     def __init__(self, config):
#         self.WaterCoilParam = DotMap(dict(WaterCoilType="CoilWaterCooling",
#                                           WaterCoilModel="CoolingDetailed"))
#         self.WaterCoilParam.update(config)
#
#         self.StateDataWaterCoils = DotMap(dict(GetWaterCoilsInputFlag=True))
#
#         self.InitWaterCoilOneTimeFlag = True
#         self.StdRhoAir = 1.225  # kg/m³
#         self.RequestingAutoSize = True
#         self.UseDesignWaterDeltaTemp = True
#
#     def SimulateWaterCoilComponents(self):
#         """
#         PURPOSE OF THIS SUBROUTINE:
#             This subroutine manages WaterCoil component simulation.
#         """
#
#         # SUBROUTINE LOCAL VARIABLE DECLARATIONS:
#         CoilNum = None  # the WaterCoil that you are currently loading input into
#         OpMode = None  # fan operating mode
#         PartLoadFrac = None  # part-load fraction of heating coil
#
#         if self.StateDataWaterCoils.GetWaterCoilsInputFlag:  # First time subroutine has been entered
#
#
#
#
#         # With the correct CoilNum Initialize
#         self._InitWaterCoil()  # Initialize all WaterCoil related parameters
#
#     def _InitWaterCoil(self):
#         """
#         PURPOSE OF THIS SUBROUTINE:
#             This subroutine is for initializations of the WaterCoil Components.
#
#         METHODOLOGY EMPLOYED:
#             Uses the status flags to trigger initializations.
#         """
#
#         # SUBROUTINE PARAMETER DEFINITIONS
#         SmallNo = 1.e-9  # SmallNo number in place of zero
#         itmax = int(10)
#         MaxIte = int(500)  # Maximum number of iterations
#
#         # SUBROUTINE LOCAL VARIABLE DECLARATIONS
#         tempCoilNum = None  # loop variable
#         DesInletAirEnth = None  # Entering air enthalpy at rating (J/kg)
#         DesOutletAirEnth = None  # Leaving air enthalpy at rating(J/kg)
#         DesAirApparatusDewPtEnth = None  # Air enthalpy at apparatus dew point at rating(J/kg)
#         DesSatEnthAtWaterInTemp = None  # Saturated enthalpy at entering liquid temp(J/kg)
#
#         CapacitanceAir = None  # Air-side capacity rate(W/C)
#         DesAirTempApparatusDewPt = None  # Temperature apparatus dew point at design capacity
#         DesAirHumRatApparatusDewPt = None  # Humidity Ratio at apparatus dew point at design capacity
#         DesBypassFactor = None  # ByPass Factor at design condition
#         SlopeTempVsHumRatio = None  # Ratio temperature difference to humidity difference between entering and leaving air states
#         TempApparatusDewPtEstimate = None  # Estimate of TAdp from SlopeTempVsHumRatio
#         Y1 = None  # Previous values of dependent variable in ITERATE
#         X1 = None  # Previous values of independent variable in ITERATE
#         error = None  # Deviation of dependent variable in iteration
#         iter = None  # Iteration counter
#         icvg = None  # Iteration convergence flag
#         ResultX = None  # Output variable from ITERATE function.
#         Ipass = None  # loop index for App_Dewpoint_Loop
#         AirInletNode = None  #
#         WaterInletNode = None  #
#         WaterOutletNode = None  #
#         FinDiamVar = None  #
#         TubeToFinDiamRatio = None  #
#         CpAirStd = None  # specific heat of air at std conditions
#         SolFla = None  # Flag of solver
#         UA0 = None  # lower bound for UA
#         UA1 = None  # upper bound for UA
#         UA = None  #
#         DesUACoilExternalEnth = None  # enthalpy based UAExternal for wet coil surface {kg/s}
#         LogMeanEnthDiff = None  # long mean enthalpy difference {J/kg}
#         LogMeanTempDiff = None  # long mean temperature difference {C}
#         DesOutletWaterTemp = None  #
#         DesSatEnthAtWaterOutTemp = None  #
#         DesEnthAtWaterOutTempAirInHumRat = None  #
#         DesEnthWaterOut = None  #
#         Cp = None  # local fluid specific heat
#         rho = None  # local fluid density
#         errFlag = None  #
#         EnthCorrFrac = 0.0  # enthalpy correction factor
#         TempCorrFra = 0.0  # temperature correction factor
#
#         MySizeFlag = True
#
#         if self.InitWaterCoilOneTimeFlag:
#             DesCpAir = 0.0
#             DesUARangeCheck = 0.0
#             MyEnvrnFlag = True
#             MySizeFlag = True
#             CoilWarningOnceFlag = True
#             MyUAAndFlowCalcFlag = True
#             MyCoilDesignFlag = True
#             MyCoilReportFlag = True
#             InitWaterCoilOneTimeFlag = False
#             PlantLoopScanFlag = True
#
#         if MySizeFlag:
#             self._SizeWaterCoil()
#             MySizeFlag = False
#
#     def _SizeWaterCoil(self):
#         """
#         PURPOSE OF THIS SUBROUTINE:
#             This subroutine is for sizing Water Coil Components for which flow rates and UAs have not been
#             specified in the input.
#
#         METHODOLOGY EMPLOYED:
#             Obtains flow rates from the zone or system sizing arrays and plant sizing data. UAs are
#             calculated by numerically inverting the individual coil calculation routines.
#         """
#
#         rho = None
#         CompType = None  # component type
#         SizingString = None  # input field sizing description (e.g., Nominal Capacity)
#         TempSize = None  # autosized value
#         DesCoilWaterInTempSaved = None  # coil water inlet temp used for error checking UA sizing
#         DesCoilInletWaterTempUsed = 0.0  # coil design inlet water temp for UA sizing only
#         Cp = None
#
#         ErrorsFound = False
#         LoopErrorsFound = False
#         PltSizCoolNum = 0
#         PltSizHeatNum = 0
#         DesCoilAirFlow = 0.0
#         DesCoilExitTemp = 0.0
#         CpAirStd = Psychometric.PsyCpAirFnW(0.0)
#
#         if (self.WaterCoilParam.WaterCoilType == "CoilWaterCooling" or self.WaterCoilParam.WaterCoilType == "CoilWaterDetailedFlatCooling") and self.RequestingAutoSize:
#             PltSizCoolNum = True
#
#         if self.WaterCoilParam.WaterCoilType == "CoilWaterCooling" or self.WaterCoilParam.WaterCoilType == "CoilWaterDetailedFlatCooling":  # Cooling
#             if self.UseDesignWaterDeltaTemp:
#                 DataWaterCoilSizCoolDeltaT = self.WaterCoilParam.designWaterTemperatureDifference
#             else:
#                  if PltSizCoolNum > 0:
#                      "state.dataSize->DataWaterCoilSizCoolDeltaT = state.dataSize->PlantSizData(PltSizCoolNum).DeltaT"  # ???
#
#         if PltSizCoolNum > 0:
#
#             if self.WaterCoilParam.WaterCoilModel == "CoolingDetailed":  # 'DETAILED FLAT FIN'
#                 CompType = "Coil_CoolingWaterDetailed"  # Coil:Cooling:Water:DetailedGeometry
#             else:
#                 CompType = "Coil_CoolingWater"  # Coil:Cooling:Water
#
#             """
#             do not print this sizing request since the autosized value is needed and this input may not be autosized (we
#             should print this!)
#             """
#             bPRINT = False
#             TempSize = self.WaterCoilParam.designAirFlowRate
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#     @staticmethod
#     def get_fluid_property(fluid_name, temperature, property_type):
#         try:
#             # Convert temperature to Kelvin
#             temperature_K = temperature + 273.15  # Assuming input temperature is in Celsius
#
#             # Define property mapping
#             property_map = {
#                 'density': 'D',
#                 'specific_heat': 'C'
#             }
#
#             # Check if the property type is valid
#             if property_type not in property_map:
#                 raise ValueError(f"Invalid property type: {property_type}")
#
#             # Get the property
#             prop = PropsSI(property_map[property_type], 'T', temperature_K, 'P', 101325, fluid_name)
#
#             return prop
#         except ValueError as e:
#             logger.error(f"Error: {e:.2f}")
#             return None
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# if __name__ == "__main__":
#
#     config_spec = DotMap({
#         "designWaterFlowRate": 0.82,
#         "designAirFlowRate": 135.28,
#         "designInletWaterTemperature": 10.3,
#         "designInletAirTemperature": 31.84,
#         "designOutletAirTemperature": 15.43,
#         "designInletAirHumidityRatio": 0.02,
#         "designOutletAirHumidityRatio": 0.01,
#         "typeOfAnalysis": "simpleanalysis",
#         "heatExchangerConfiguration": "counterflow",
#         "designWaterTemperatureDifference": 15.0
#     })
#
#     coil = WaterCoils(config_spec)
#     coil._SizeWaterCoil()
#
