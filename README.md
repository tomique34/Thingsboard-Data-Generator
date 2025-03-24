# Thingsboard Data Generator

### Author: Tomas Vince
### Version: 1.0

A Flask web application for generating random data for Thingsboard devices. This tool allows users to:

1. Create device profiles with custom attributes
2. Generate random data for these attributes within defined ranges
3. Send the generated data to a Thingsboard server (Professional Edition)

## Features

- User-friendly web interface
- Custom attribute definition
- Random data generation with configurable ranges
- Import/Export device profiles in JSON format
- Integration with Thingsboard REST API
- Secure credential handling through environment variables

## Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your Thingsboard credentials (see `.env.example`)
6. Run the application: `python app.py`

## Usage

1. Access the web interface at http://localhost:5000
2. Configure your Thingsboard connection
3. Create device profiles with attributes
4. Generate and send data to Thingsboard

### Working with Device Profiles

#### Importing Profiles

You can import device profiles from a JSON file by clicking the "Import" button on the Device Profiles page. The JSON file must have the following structure:

```json
{
  "profiles": [
    {
      "name": "Profile Name",
      "attributes": [
        {
          "name": "attribute_name",
          "type": "number|integer|string|boolean",
          "min_value": minimum_value_for_numeric_types,
          "max_value": maximum_value_for_numeric_types,
          "options": ["option1", "option2"] // For string type with predefined options
        },
        // More attributes...
      ]
    },
    // More profiles...
  ]
}
```

See the `example_profiles.json` file in the project for complete examples.

#### Exporting Profiles

You can export all device profiles or individual profiles to a JSON file for backup or sharing purposes:

- Export all profiles by clicking the "Export All" button on the Device Profiles page
- Export a specific profile by clicking the "Export" button on a profile card

## License

MIT
