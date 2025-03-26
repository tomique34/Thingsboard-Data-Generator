# Device Profiles Templates

This directory contains ready-to-use device profile templates for the Thingsboard Data Generator. These templates can be imported directly into the application to quickly set up common IoT device profiles with enhanced persistent attributes and metadata support.

## Available Templates

1. **Temperature_Sensor.json** - Basic temperature and humidity sensor with battery level
2. **Smart_Light.json** - Smart lighting device with brightness and color temperature control
3. **Water_Quality_Sensor.json** - Comprehensive water quality monitoring device
4. **Air_Quality_Sensor.json** - Air quality monitoring device with various pollution metrics
5. **Smart_Thermostat.json** - Smart HVAC controller with temperature and mode settings
6. **Energy_Meter.json** - Electrical energy consumption monitoring device
7. **GPS_Tracker.json** - Location tracking device with GPS coordinates and status
8. **Motion_Sensor.json** - Motion detection sensor with additional environmental metrics

## New Features: Persistent Attributes and Metadata

### Persistent Attributes
Persistent attributes are now supported, allowing you to:
- Define static or rarely changing device characteristics
- Maintain consistent device-specific information across sessions
- Store metadata that doesn't change with each telemetry update

### Metadata Enhancements
- Expanded metadata support for more detailed device profile description
- Version tracking for device profile templates
- Additional contextual information for better device management

## How to Use

To import a device profile template:

1. From the main interface, click the "Import" button in the Device Profiles section
2. Select the desired template JSON file from this directory
3. Choose whether to overwrite existing profiles with the same name
4. Click "Import" to load the profile

## Customizing Templates

You can modify these templates or create your own by following this enhanced structure:

```json
{
  "profiles": [
    {
      "name": "Your Device Name",
      "persistent_attributes": [
        {
          "name": "device_location",
          "type": "string",
          "value": "Main Building, Floor 2"
        },
        {
          "name": "installation_date",
          "type": "string",
          "value": "2024-03-26"
        }
      ],
      "telemetry_attributes": [
        {
          "name": "temperature",
          "type": "number",
          "min_value": -50,
          "max_value": 100
        }
      ]
    }
  ],
  "metadata": {
    "exported_at": "timestamp",
    "version": "2.0",
    "description": "Enhanced device profile with persistent attributes",
    "device_type": "environmental_sensor",
    "manufacturer": "Your Company Name",
    "compatibility": ["ThingsBoard PE", "IoT Platform"]
  }
}
```

## Attribute Types

- **Persistent Attributes**:
  - Remain constant or change infrequently
  - Stored separately from frequently changing telemetry data
  - Useful for device-specific configuration and identification

- **Telemetry Attributes**:
  - **number**: Floating-point values (temperature, humidity, etc.)
  - **integer**: Whole number values (count, level, etc.)
  - **string**: Text values, with optional predefined options (mode, state, etc.)
  - **boolean**: True/false values (on/off, detected/not detected, etc.)

## Best Practices

- Use persistent attributes for:
  - Device location
  - Installation dates
  - Manufacturer information
  - Static configuration settings

- Use telemetry attributes for:
  - Sensor readings
  - Current device state
  - Frequently changing measurements

For more information on creating custom device profiles and utilizing persistent attributes, refer to the main application documentation.