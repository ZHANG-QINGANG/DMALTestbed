class OnOffTemperatureController:
    def __init__(self, setpoint, tolerance):
        """
        Initialize the controller with a target setpoint and tolerance.

        :param setpoint: Target room temperature in Celsius.
        :param tolerance: Allowed deviation from the setpoint (deadband).
        """
        self.setpoint = setpoint
        self.tolerance = tolerance
        self.heating_on = False
        self.cooling_on = False

    def update(self, current_temperature):
        """
        Update the controller state based on the current target.

        :param current_temperature: The current temperature in the room (Celsius).
        :return: A string indicating the action of the controller.
        """
        # Define the boundaries for heating and cooling based on setpoint and tolerance
        lower_threshold = self.setpoint - self.tolerance
        upper_threshold = self.setpoint + self.tolerance

        # Turn on heating if the temperature is below the lower threshold
        if current_temperature < lower_threshold:
            self.heating_on = True
            self.cooling_on = False
            return f"Heating ON: Room temperature ({current_temperature}°C) is below {lower_threshold}°C."

        # Turn on cooling if the temperature is above the upper threshold
        elif current_temperature > upper_threshold:
            self.heating_on = False
            self.cooling_on = True
            return f"Cooling ON: Room temperature ({current_temperature}°C) is above {upper_threshold}°C."

        # If the temperature is within the tolerance range, turn off both heating and cooling
        else:
            self.heating_on = False
            self.cooling_on = False
            return f"System OFF: Room temperature ({current_temperature}°C) is within the comfort range."


# Example usage
if __name__ == "__main__":
    # Define the setpoint temperature (22°C) and tolerance (1°C)
    controller = OnOffTemperatureController(setpoint=22.0, tolerance=1.0)

    # Simulated room temperatures
    temperatures = [20.5, 21.0, 22.0, 23.5, 24.0, 21.5, 19.5]

    for temp in temperatures:
        action = controller.update(temp)
        print(action)
