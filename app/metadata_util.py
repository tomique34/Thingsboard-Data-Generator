"""
Metadata generation utility for Thingsboard Data Generator.
This module provides functions to generate metadata based on telemetry data.
"""

def generate_tank_metadata(telemetry):
    """
    Generate metadata for Tank devices based on telemetry values.
    This function implements the rule logic from the Thingsboard rule chain.
    
    Args:
        telemetry (dict): Telemetry data with keys like 'temperature', 'battery', 'fuelLevel', etc.
        
    Returns:
        dict: Metadata key-value pairs
    """
    metadata = {}
    
    # Check temperature alarms
    if 'temperature' in telemetry:
        temp = telemetry['temperature']
        metadata['isHighTemperatureAlarms'] = temp > 30
        metadata['isLowTemperature'] = temp < 5
        metadata['isHighTemperature'] = temp > 25
    
    # Check battery level
    if 'battery' in telemetry:
        battery = telemetry['battery']
        metadata['isLowBattery'] = battery < 20
    
    # Check fuel level
    if 'fuelLevel' in telemetry:
        fuel = telemetry['fuelLevel']
        metadata['isLowFuel'] = fuel < 10
    
    # Calculate active status based on the rule chain logic
    has_low_battery = metadata.get('isLowBattery', False)
    has_low_fuel = metadata.get('isLowFuel', False)
    has_temp_issue = metadata.get('isLowTemperature', False) or metadata.get('isHighTemperature', False)
    has_high_temp_alarm = metadata.get('isHighTemperatureAlarms', False)
    
    metadata['isNoAlarms'] = not (has_low_battery and has_low_fuel and has_temp_issue)
    
    # Set the active status based on alarms
    metadata['active'] = not (has_high_temp_alarm and has_low_battery and has_low_fuel and has_temp_issue)
    
    # Add last activity time
    metadata['lastActivityTime'] = int(telemetry.get('ts', 0))
    
    return metadata

def get_metadata_generator(profile_name):
    """
    Get the appropriate metadata generator function based on the device profile name.
    
    Args:
        profile_name (str): Name of the device profile
        
    Returns:
        function: A function that generates metadata for the given profile
    """
    # For now, we only have a tank metadata generator
    if 'tank' in profile_name.lower():
        return generate_tank_metadata
    
    # Default generator that returns empty metadata
    return lambda x: {}
