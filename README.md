# Thingsboard Data Generator

### Author: Tomas Vince
### Version: 1.0

A Flask web application for generating random data for Thingsboard devices. This tool allows users to:

1. Create device profiles with custom attributes
2. Generate random data for these attributes within defined ranges
3. Send the generated data to a Thingsboard server (Professional Edition)
4. Automatically generate data at specified intervals for both single devices and multiple devices

## Features

- User-friendly web interface
- Custom attribute definition
- Random data generation with configurable ranges
- Automatic data generation at user-defined intervals
- Import/Export device profiles in JSON format
- Integration with Thingsboard REST API
- Secure credential handling through environment variables
- Docker and Kubernetes support

## Installation

### Standard Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your Thingsboard credentials (see `.env.example`)
6. Run the application: `python app.py`

### Docker Installation

#### Using Docker Compose (Recommended)

1. Clone this repository
2. Copy `.env.example` to `.env` and edit the values for your Thingsboard instance
3. Run the application with Docker Compose:
   ```
   docker-compose up -d
   ```
4. Access the web interface at http://localhost:5001

#### Using Docker Directly

1. Clone this repository
2. Build the Docker image:
   ```
   docker build -t thingsboard-data-generator .
   ```
3. Run the Docker container:
   ```
   docker run -p 5001:5001 --env-file .env -d thingsboard-data-generator
   ```
4. Access the web interface at http://localhost:5001

### Kubernetes Deployment

1. Build and push the Docker image to your container registry:
   ```
   docker build -t your-registry/thingsboard-data-generator:latest .
   docker push your-registry/thingsboard-data-generator:latest
   ```

2. Create a Kubernetes ConfigMap or Secret for environment variables:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: thingsboard-data-generator-config
   data:
     TB_HOST: "http://your-thingsboard-host"
     TB_PORT: "8080"
     TB_USERNAME: "your-username"
     TB_PASSWORD: "your-password"
     FLASK_SECRET_KEY: "your-secret-key"
     FLASK_DEBUG: "False"
   ```

3. Create a Kubernetes Deployment:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: thingsboard-data-generator
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: thingsboard-data-generator
     template:
       metadata:
         labels:
           app: thingsboard-data-generator
       spec:
         containers:
         - name: thingsboard-data-generator
           image: your-registry/thingsboard-data-generator:latest
           ports:
           - containerPort: 5001
           envFrom:
           - configMapRef:
               name: thingsboard-data-generator-config
   ```

4. Create a Kubernetes Service:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: thingsboard-data-generator
   spec:
     selector:
       app: thingsboard-data-generator
     ports:
     - port: 80
       targetPort: 5001
     type: ClusterIP
   ```

5. Optional: Create an Ingress resource for external access

## Usage

1. Access the web interface at http://localhost:5001
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

### Automatic Data Generation

The application supports two methods of automatic data generation:

#### Single Device Auto-Generation

When viewing a specific device profile:

1. Enter the device name and data type (telemetry or attributes)
2. Set the desired generation interval (in seconds, minutes, or hours)
3. Click "Start Auto-Generate" to begin sending data at the specified interval
4. The system will continuously generate and send random data based on the profile's attribute definitions
5. View real-time statistics including:
   - Total messages sent
   - Running time
   - Next generation countdown
6. Click "Stop Auto-Generate" to end the automatic generation process

This feature is ideal for testing individual devices with consistent data generation patterns.

#### Multiple Device Auto-Generation

For generating data across multiple devices simultaneously:

1. From the Device Profiles page, click "Autonomous Generation"
2. Select multiple device profiles you want to generate data for
3. Configure generation settings, including:
   - Device name prefix (optional)
   - Interval for data generation
   - Data type (telemetry or attributes)
4. Start the generation process to send data to all selected devices
5. Monitor the generation process with statistics for all devices
6. Stop the process when testing is complete

This feature is perfect for simulating multi-device environments and testing system scaling.

## Docker Configuration Options

The Docker image supports the following environment variables:

- `TB_HOST`: Thingsboard host URL (default: http://localhost)
- `TB_PORT`: Thingsboard port (default: 8080)
- `TB_USERNAME`: Thingsboard username (default: tenant@thingsboard.org)
- `TB_PASSWORD`: Thingsboard password (default: tenant)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions (default: dev-key-change-me)
- `FLASK_DEBUG`: Debug mode (default: False)

You can set these in your `.env` file or directly in the `docker-compose.yml` file.

## License

MIT
