from CoolProp.CoolProp import PropsSI


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
        print(f"Error: {e}")
        return None


# Usage example
temperature = 18

# Get density
rho = get_fluid_property(
    "water",
    temperature,
    'density',
)

# Get specific heat
Cp = get_fluid_property(
    "water",
    temperature,
    'specific_heat'
)

print(f"rho = {rho}. Cp = {Cp}")

