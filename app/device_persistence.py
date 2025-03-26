"""
Device Persistence Utility for Thingsboard Data Generator.
This module provides functions to manage persistent device attributes.
"""
import os
import json
import time
from datetime import datetime

# File to store device attributes
PERSISTENCE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'device_attributes.json')

def load_device_attributes():
    """
    Load all device attributes from the persistence file.
    
    Returns:
        dict: Device attributes keyed by device name
    """
    if not os.path.exists(PERSISTENCE_FILE):
        return {}
        
    try:
        with open(PERSISTENCE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_device_attributes(devices_data):
    """
    Save device attributes to the persistence file.
    
    Args:
        devices_data (dict): Device attributes keyed by device name
    """
    try:
        with open(PERSISTENCE_FILE, 'w') as f:
            json.dump(devices_data, f, indent=2)
    except IOError as e:
        print(f"Error saving device attributes: {e}")

def get_device_attributes(device_name):
    """
    Get attributes for a specific device.
    
    Args:
        device_name (str): Name of the device
        
    Returns:
        dict: Device attributes or empty dict if not found
    """
    devices_data = load_device_attributes()
    return devices_data.get(device_name, {})

def update_device_attributes(device_name, attributes, scope='client'):
    """
    Update attributes for a specific device.
    
    Args:
        device_name (str): Name of the device
        attributes (dict): Attributes to update
        scope (str): Attribute scope ('client' or 'server')
        
    Returns:
        dict: Updated device attributes
    """
    devices_data = load_device_attributes()
    
    # Initialize device entry if it doesn't exist
    if device_name not in devices_data:
        devices_data[device_name] = {
            'client': {},
            'server': {},
            'last_updated': int(time.time() * 1000)
        }
    
    # Update attributes in the specified scope
    if scope in ['client', 'server']:
        devices_data[device_name][scope].update(attributes)
        devices_data[device_name]['last_updated'] = int(time.time() * 1000)
    
    # Save updated data
    save_device_attributes(devices_data)
    
    return devices_data[device_name]

def initialize_device_attributes(device_name, profile):
    """
    Initialize attributes for a device based on profile defaults.
    Only sets attributes that don't already exist.
    
    Args:
        device_name (str): Name of the device
        profile (dict): Device profile with default attribute values
        
    Returns:
        dict: Initialized device attributes
    """
    # Load current attributes
    device_attrs = get_device_attributes(device_name)
    
    # Initialize client attributes if present in profile
    if 'client_attributes' in profile:
        if 'client' not in device_attrs:
            device_attrs['client'] = {}
            
        for attr in profile['client_attributes']:
            # Only set if attribute doesn't exist
            if attr['name'] not in device_attrs['client'] and 'default_value' in attr:
                device_attrs['client'][attr['name']] = attr['default_value']
    
    # Initialize server attributes if present in profile
    if 'server_attributes' in profile:
        if 'server' not in device_attrs:
            device_attrs['server'] = {}
            
        for attr in profile['server_attributes']:
            # Only set if attribute doesn't exist
            if attr['name'] not in device_attrs['server'] and 'default_value' in attr:
                device_attrs['server'][attr['name']] = attr['default_value']
    
    # Update the device's attributes
    devices_data = load_device_attributes()
    devices_data[device_name] = device_attrs
    devices_data[device_name]['last_updated'] = int(time.time() * 1000)
    save_device_attributes(devices_data)
    
    return device_attrs
