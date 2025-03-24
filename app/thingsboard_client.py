import requests
import json
import time
import logging
from tb_rest_client.rest_client_pe import RestClientPE
from tb_rest_client.rest import ApiException

class ThingsboardClient:
    """Client for interacting with Thingsboard REST API"""
    
    def __init__(self, host, port, username, password):
        """Initialize the client with connection details"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.base_url = f"{host}:{port}"
        self.client = RestClientPE(base_url=self.base_url)
        self.logged_in = False
    
    def login(self):
        """Login to Thingsboard"""
        try:
            self.client.login(username=self.username, password=self.password)
            self.logged_in = True
            return True
        except Exception as e:
            logging.error(f"Login failed: {e}")
            self.logged_in = False
            raise Exception(f"Login failed: {e}")
    
    def is_logged_in(self):
        """Check if client is logged in"""
        return self.logged_in
    
    def get_auth_token(self):
        """Get the authentication token"""
        # Try various ways to get the token
        if hasattr(self.client, 'token'):
            return self.client.token
        elif hasattr(self.client, 'auth_token'):
            return self.client.auth_token
        elif hasattr(self.client, 'get_token'):
            return self.client.get_token()
        
        # As a last resort, try to get it by logging in again
        try:
            self.login()
            if hasattr(self.client, 'token'):
                return self.client.token
        except Exception as e:
            logging.error(f"Error getting auth token: {e}")
        
        raise Exception("Could not get authentication token")
    
    def get_or_create_device(self, device_name):
        """Get a device by name or create it if it doesn't exist"""
        if not self.logged_in:
            self.login()
        
        try:
            # Print available methods in REST client
            print(f"DEBUG: Available methods in client: {dir(self.client)}")
            
            # Try to find the device by name
            devices = self.client.get_tenant_devices(text_search=device_name, page_size=10, page=0)
            
            for device in devices.data:
                if device.name == device_name:
                    print(f"DEBUG: Found existing device: {device}")
                    print(f"DEBUG: Device ID: {device.id}")
                    # Extract the ID from the device object
                    if hasattr(device, 'id') and hasattr(device.id, 'id'):
                        device_id = device.id.id
                    else:
                        device_id = device.id
                    return {'id': device_id, 'name': device_name}
            
            # Device not found, create it
            try:
                default_device_profile_id = self.client.get_default_device_profile_info().id
                
                # Check different methods for device creation
                if hasattr(self.client, 'save_device'):
                    device = self.client.save_device({
                        "name": device_name,
                        "type": "DataGenerator",
                        "device_profile_id": default_device_profile_id
                    })
                elif hasattr(self.client, 'create_device'):
                    device = self.client.create_device(device_name, "DataGenerator", default_device_profile_id)
                else:
                    # Use direct REST API
                    url = f"{self.base_url}/api/device"
                    headers = {
                        'Content-Type': 'application/json',
                        'X-Authorization': f'Bearer {self.get_auth_token()}'
                    }
                    data = {
                        "name": device_name,
                        "type": "DataGenerator",
                        "deviceProfileId": default_device_profile_id
                    }
                    response = requests.post(url, headers=headers, json=data)
                    if response.status_code != 200:
                        raise Exception(f"HTTP Error: {response.status_code} - {response.text}")
                    device = response.json()
                
                print(f"DEBUG: Created new device: {device}")
                print(f"DEBUG: Device type: {type(device)}")
                
                # Extract the ID from the new device
                if hasattr(device, 'id') and hasattr(device.id, 'id'):
                    device_id = device.id.id
                elif hasattr(device, 'id'):
                    device_id = device.id
                elif isinstance(device, dict) and 'id' in device:
                    if isinstance(device['id'], dict) and 'id' in device['id']:
                        device_id = device['id']['id']
                    else:
                        device_id = device['id']
                else:
                    # Last resort - try to get it as a string representation
                    device_id = str(device).split('id=')[1].split(',')[0].strip()
                
                print(f"DEBUG: Extracted device ID: {device_id}")
                return {'id': device_id, 'name': device_name}
            except Exception as e:
                print(f"ERROR creating device: {e}")
                raise e
                
        except Exception as e:
            logging.error(f"Error getting/creating device: {e}")
            raise Exception(f"Error getting/creating device: {e}")
    
    def send_attributes(self, device_id, attributes):
        """Send attributes to a device"""
        if not self.logged_in:
            self.login()
        
        try:
            # Print debug info to help troubleshoot
            print(f"DEBUG: Using device_id for attributes: {device_id}")
            print(f"DEBUG: Sending attributes: {attributes}")
            
            # Try alternative methods for sending attributes
            if hasattr(self.client, 'save_device_attributes'):
                self.client.save_device_attributes(device_id, "SERVER_SCOPE", attributes)
            elif hasattr(self.client, 'set_device_attributes'):
                self.client.set_device_attributes(device_id, attributes)
            elif hasattr(self.client, 'publish_attributes'):
                self.client.publish_attributes(device_id, attributes)
            else:
                # Last resort - try to use the REST API directly
                base_url = self.base_url
                url = f"{base_url}/api/plugins/telemetry/DEVICE/{device_id}/SERVER_SCOPE"
                headers = {
                    'Content-Type': 'application/json',
                    'X-Authorization': f'Bearer {self.get_auth_token()}'
                }
                response = requests.post(url, headers=headers, json=attributes)
                if response.status_code != 200:
                    raise Exception(f"HTTP Error: {response.status_code} - {response.text}")
                
            return True
        except Exception as e:
            logging.error(f"Error sending attributes: {e}")
            raise Exception(f"Error sending attributes: {e}")
    
    def send_telemetry(self, device_id, telemetry, timestamp=None):
        """Send telemetry to a device"""
        if not self.logged_in:
            self.login()
        
        try:
            # Add timestamp if not provided
            if timestamp is None:
                timestamp = int(time.time() * 1000)  # Current time in milliseconds
            
            # Format the telemetry data
            telemetry_data = {
                "ts": timestamp,
                "values": telemetry
            }
            
            # Print debug info to help troubleshoot
            print(f"DEBUG: Using device_id: {device_id}")
            print(f"DEBUG: Sending telemetry: {telemetry_data}")
            print(f"DEBUG: Client methods: {dir(self.client)}")
            
            # Try alternative methods for sending telemetry
            if hasattr(self.client, 'save_device_telemetry'):
                self.client.save_device_telemetry(device_id, "DEVICE_SCOPE", telemetry_data)
            elif hasattr(self.client, 'send_telemetry'):
                self.client.send_telemetry(device_id, telemetry_data)
            elif hasattr(self.client, 'publish_telemetry'):
                self.client.publish_telemetry(device_id, telemetry_data)
            else:
                # Last resort - try to use the REST API directly
                base_url = self.base_url
                url = f"{base_url}/api/plugins/telemetry/DEVICE/{device_id}/timeseries/ANY"
                headers = {
                    'Content-Type': 'application/json',
                    'X-Authorization': f'Bearer {self.get_auth_token()}'
                }
                # For direct API call, we don't need to wrap in ts/values
                response = requests.post(url, headers=headers, json=telemetry)
                if response.status_code != 200:
                    raise Exception(f"HTTP Error: {response.status_code} - {response.text}")
            
            return True
        except Exception as e:
            logging.error(f"Error sending telemetry: {e}")
            raise Exception(f"Error sending telemetry: {e}")
    
    def get_device_profiles(self):
        """Get all device profiles"""
        if not self.logged_in:
            self.login()
        
        try:
            return self.client.get_device_profiles(page_size=100, page=0)
        except Exception as e:
            logging.error(f"Error getting device profiles: {e}")
            raise Exception(f"Error getting device profiles: {e}")
