# Device Profiles Templates

This directory contains ready-to-use device profile templates for the Thingsboard Data Generator. These templates can be imported directly into the application to quickly set up common IoT device profiles.

## Available Templates

1. **Temperature_Sensor.json** - Basic temperature and humidity sensor with battery level
2. **Smart_Light.json** - Smart lighting device with brightness and color temperature control
3. **Water_Quality_Sensor.json** - Comprehensive water quality monitoring device
4. **Air_Quality_Sensor.json** - Air quality monitoring device with various pollution metrics
5. **Smart_Thermostat.json** - Smart HVAC controller with temperature and mode settings
6. **Energy_Meter.json** - Electrical energy consumption monitoring device
7. **GPS_Tracker.json** - Location tracking device with GPS coordinates and status
8. **Motion_Sensor.json** - Motion detection sensor with additional environmental metrics

## How to Use

To import a device profile template:

1. From the main interface, click the "Import" button in the Device Profiles section
2. Select the desired template JSON file from this directory
3. Choose whether to overwrite existing profiles with the same name
4. Click "Import" to load the profile

## Customizing Templates

You can modify these templates or create your own by following this structure:

```json
{
  "profiles": [
    {
      "name": "Your Device Name",
      "attributes": [
        {
          "name": "attribute_name",
          "type": "number|integer|string|boolean",
          "min_value": minimum_value_for_numeric_types,
          "max_value": maximum_value_for_numeric_types,
          "options": ["option1", "option2"] 
        }
      ]
    }
  ],
  "metadata": {
    "exported_at": "timestamp",
    "version": "1.0",
    "description": "Description of your device profile"
  }
}
```

## Attribute Types

- **number**: Floating-point values (temperature, humidity, etc.)
- **integer**: Whole number values (count, level, etc.)
- **string**: Text values, with optional predefined options (mode, state, etc.)
- **boolean**: True/false values (on/off, detected/not detected, etc.)

For more information on creating custom device profiles, refer to the main application documentation.
