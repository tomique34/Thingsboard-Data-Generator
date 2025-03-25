import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, send_file, Response
from werkzeug.utils import secure_filename
from app.forms import DeviceProfileForm, AttributeForm, GenerateDataForm, ConnectionForm, AutonomousGenerationForm
from app.thingsboard_client import ThingsboardClient
import random
import json
import traceback
from datetime import datetime
import time
import tempfile
import uuid

# Create blueprint
main = Blueprint('main', __name__)

# Store device profiles in memory as a list (would be better to use a database in production)
profile_data = []
current_profile = None
tb_client = None


@main.route('/', methods=['GET', 'POST'])
def index():
    global tb_client
    form = ConnectionForm()
    
    if form.validate_on_submit():
        try:
            # Create ThingsBoard client
            tb_client = ThingsboardClient(
                host=form.host.data,
                port=form.port.data,
                username=form.username.data,
                password=form.password.data
            )
            
            # Test connection
            tb_client.login()
            flash('Successfully connected to ThingsBoard!', 'success')
            return redirect(url_for('main.device_profiles'))
        except Exception as e:
            flash(f'Connection error: {str(e)}', 'danger')
            tb_client = None
    else:
        # Pre-fill form with values from config
        form.host.data = current_app.config.get('TB_HOST')
        form.port.data = current_app.config.get('TB_PORT')
        form.username.data = current_app.config.get('TB_USERNAME')
        form.password.data = current_app.config.get('TB_PASSWORD')
    
    return render_template('index.html', form=form)


@main.route('/device-profiles', methods=['GET'])
def device_profiles():
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
        
    # Explicitly create a list to ensure we're passing the right type
    print(f"DEBUG: profile_data type: {type(profile_data)}")
    print(f"DEBUG: profile_data content: {profile_data}")
    
    return render_template('device_profiles.html', profiles=profile_data)


@main.route('/export-profiles', methods=['GET'])
def export_profiles():
    """Export all device profiles as JSON
    
    Creates a JSON file with all device profiles and metadata,
    then sends it as a downloadable attachment.
    """
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
    
    # Create a JSON representation of all profiles
    export_data = {
        'profiles': profile_data,
        'metadata': {
            'exported_at': datetime.now().isoformat(),
            'version': '1.0'
        }
    }
    
    # Create a temporary file to store the JSON
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_filename = temp_file.name
    
    with open(temp_filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    # Send the file as an attachment
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_name = f"thingsboard_profiles_{timestamp}.json"
    
    return send_file(
        temp_filename,
        as_attachment=True,
        download_name=download_name,
        mimetype='application/json'
    )


@main.route('/export-profile/<profile_name>', methods=['GET'])
def export_profile(profile_name):
    """Export a single device profile as JSON
    
    Creates a JSON file with a single device profile and metadata,
    then sends it as a downloadable attachment.
    """
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
    
    # Find the profile
    profile = None
    for p in profile_data:
        if p['name'] == profile_name:
            profile = p
            break
    
    if not profile:
        flash(f'Profile "{profile_name}" not found', 'danger')
        return redirect(url_for('main.device_profiles'))
    
    # Create a JSON representation of the profile
    export_data = {
        'profiles': [profile],
        'metadata': {
            'exported_at': datetime.now().isoformat(),
            'version': '1.0'
        }
    }
    
    # Create a temporary file to store the JSON
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_filename = temp_file.name
    
    with open(temp_filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    # Send the file as an attachment
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_name = f"{profile_name}_{timestamp}.json"
    
    return send_file(
        temp_filename,
        as_attachment=True,
        download_name=download_name,
        mimetype='application/json'
    )


@main.route('/import-profiles', methods=['POST'])
def import_profiles():
    """Import device profiles from a JSON file
    
    Accepts a JSON file upload containing device profiles.
    Validates the structure and adds profiles to the current session.
    Can optionally overwrite existing profiles with the same name.
    """
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
    
    # Check if a file was uploaded
    if 'profile_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('main.device_profiles'))
    
    file = request.files['profile_file']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('main.device_profiles'))
    
    # Check if the file is a JSON file
    if not file.filename.endswith('.json'):
        flash('File must be a JSON file', 'danger')
        return redirect(url_for('main.device_profiles'))
    
    # Parse the JSON file
    try:
        # Debug information
        print(f"DEBUG: Processing import request with form data: {request.form}")
        print(f"DEBUG: File received: {file.filename}")
        
        import_data = json.load(file)
        
        # Validate the structure of the import data
        if 'profiles' not in import_data:
            flash('Invalid JSON structure: missing "profiles" key', 'danger')
            return redirect(url_for('main.device_profiles'))
        
        # Check if we should overwrite existing profiles
        overwrite_existing = 'overwrite_existing' in request.form
        
        # Import each profile
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        
        for profile in import_data['profiles']:
            # Validate profile structure
            if 'name' not in profile or 'attributes' not in profile:
                flash(f'Skipping invalid profile: missing name or attributes', 'warning')
                skipped_count += 1
                continue
            
            # Check if a profile with this name already exists
            existing_profile = None
            for idx, p in enumerate(profile_data):
                if p['name'] == profile['name']:
                    existing_profile = idx
                    break
            
            if existing_profile is not None:
                if overwrite_existing:
                    # Update the existing profile
                    profile_data[existing_profile] = profile
                    updated_count += 1
                else:
                    # Skip this profile
                    skipped_count += 1
            else:
                # Add the new profile
                profile_data.append(profile)
                imported_count += 1
        
        # Show a success message
        if imported_count > 0 or updated_count > 0:
            message = f"Successfully imported {imported_count} new profiles"
            if updated_count > 0:
                message += f" and updated {updated_count} existing profiles"
            if skipped_count > 0:
                message += f" ({skipped_count} profiles skipped)"
            flash(message, 'success')
        else:
            flash(f"No profiles were imported ({skipped_count} profiles skipped)", 'warning')
        
        return redirect(url_for('main.device_profiles'))
    
    except json.JSONDecodeError:
        flash('Invalid JSON file', 'danger')
        return redirect(url_for('main.device_profiles'))
    except Exception as e:
        flash(f'Error importing profiles: {str(e)}', 'danger')
        print(traceback.format_exc())
        return redirect(url_for('main.device_profiles'))


@main.route('/device-profile/create', methods=['GET', 'POST'])
def create_device_profile():
    global current_profile
    
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
        
    form = DeviceProfileForm()
    
    if form.validate_on_submit():
        profile_name = form.name.data
        
        # Check if profile with this name already exists
        for profile in profile_data:
            if profile['name'] == profile_name:
                flash(f'Profile with name "{profile_name}" already exists', 'danger')
                return render_template('create_profile.html', form=form)
        
        # Create new device profile
        new_profile = {
            'name': profile_name,
            'attributes': []
        }
        profile_data.append(new_profile)
        current_profile = profile_name
        flash(f'Device profile "{profile_name}" created successfully', 'success')
        return redirect(url_for('main.edit_device_profile', profile_name=profile_name))
    
    return render_template('create_profile.html', form=form)


@main.route('/device-profile/<profile_name>/edit', methods=['GET', 'POST'])
def edit_device_profile(profile_name):
    global current_profile
    
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
        
    # Find the requested profile by name
    profile = None
    for p in profile_data:
        if p['name'] == profile_name:
            profile = p
            break
    
    if not profile:
        flash(f'Profile "{profile_name}" not found', 'danger')
        return redirect(url_for('main.device_profiles'))
    
    current_profile = profile_name
    form = AttributeForm()
    
    if form.validate_on_submit():
        attribute = {
            'name': form.name.data,
            'type': form.data_type.data,
            'min_value': form.min_value.data if form.min_value.data else None,
            'max_value': form.max_value.data if form.max_value.data else None,
            'options': form.options.data.split(',') if form.options.data else []
        }
        
        profile['attributes'].append(attribute)
        flash(f'Attribute "{form.name.data}" added successfully', 'success')
        return redirect(url_for('main.edit_device_profile', profile_name=profile_name))
    
    return render_template('edit_profile.html', profile=profile, form=form)


@main.route('/device-profile/<profile_name>/attribute/<int:attr_index>/delete', methods=['POST'])
def delete_attribute(profile_name, attr_index):
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
        
    # Find profile by name
    profile = None
    for p in profile_data:
        if p['name'] == profile_name:
            profile = p
            break
    
    if not profile:
        flash(f'Profile "{profile_name}" not found', 'danger')
        return redirect(url_for('main.device_profiles'))
    
    if attr_index < 0 or attr_index >= len(profile['attributes']):
        flash('Invalid attribute index', 'danger')
    else:
        attr_name = profile['attributes'][attr_index]['name']
        del profile['attributes'][attr_index]
        flash(f'Attribute "{attr_name}" deleted successfully', 'success')
    
    return redirect(url_for('main.edit_device_profile', profile_name=profile_name))


@main.route('/device-profile/<profile_name>/delete', methods=['POST'])
def delete_device_profile(profile_name):
    global current_profile
    
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
        
    # Find profile by name and its index
    profile_idx = -1
    for idx, p in enumerate(profile_data):
        if p['name'] == profile_name:
            profile_idx = idx
            break
    
    if profile_idx == -1:
        flash(f'Profile "{profile_name}" not found', 'danger')
    else:
        del profile_data[profile_idx]
        if current_profile == profile_name:
            current_profile = None
        flash(f'Profile "{profile_name}" deleted successfully', 'success')
    
    return redirect(url_for('main.device_profiles'))


@main.route('/device-profile/<profile_name>/generate', methods=['GET', 'POST'])
def generate_data(profile_name):
    """Generate and send data for a specific device profile"""
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
    
    # Debug incoming request
    print(f"DEBUG: Generate data request for profile: {profile_name}")
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Headers: {request.headers}")
    if request.method == 'POST':
        print(f"DEBUG: Form data: {request.form}")
    
    # Find profile by name
    profile = None
    for p in profile_data:
        if p['name'] == profile_name:
            profile = p
            break
    
    if not profile:
        error_msg = f'Profile "{profile_name}" not found'
        print(f"ERROR: {error_msg}")
        flash(error_msg, 'danger')
        return redirect(url_for('main.device_profiles'))
    
    form = GenerateDataForm()
    is_ajax_request = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        # Process the form even if validation isn't perfect (for AJAX)
        if form.validate_on_submit() or is_ajax_request:
            try:
                # Always reset the random seed to current time
                random.seed(int(time.time() * 1000))
                
                # Get device name from form
                device_name = form.device_name.data or request.form.get('device_name')
                if not device_name:
                    raise ValueError("Device name is required")
                
                # Get data type from form
                data_type = form.data_type.data or request.form.get('data_type', 'telemetry')
                
                print(f"DEBUG: Processing for device: {device_name}, data_type: {data_type}")
                
                # Create or get device
                device = tb_client.get_or_create_device(device_name)
                device_id = device['id']
                print(f"DEBUG: Device ID: {device_id}")
                
                # Generate random values for each attribute
                attributes = {}
                telemetry = {}
                timestamp = int(time.time() * 1000)  # Current time in milliseconds
                
                # Debug info for profile
                print(f"DEBUG: Profile attributes: {profile['attributes']}")
                
                for attr in profile['attributes']:
                    value = generate_random_value(attr)
                    print(f"DEBUG: Generated for {attr['name']}: {value}")
                    
                    # Attributes don't have timestamps, telemetry does
                    if data_type == 'attributes':
                        attributes[attr['name']] = value
                    else:  # telemetry
                        telemetry[attr['name']] = value
                
                print(f"DEBUG: Final data - Attributes: {attributes}, Telemetry: {telemetry}")
                
                # Send data to ThingsBoard
                success = True
                error_msg = None
                
                try:
                    if attributes:
                        print(f"DEBUG: Sending attributes to device {device_id}")
                        tb_client.send_attributes(device_id, attributes)
                        
                    if telemetry:
                        print(f"DEBUG: Sending telemetry to device {device_id}")
                        tb_client.send_telemetry(device_id, telemetry, timestamp)
                        
                    print("DEBUG: Data sent successfully!")
                except Exception as inner_e:
                    success = False
                    error_msg = str(inner_e)
                    print(f"ERROR: Failed to send data: {error_msg}")
                    print(traceback.format_exc())
                
                # Return response based on request type
                if is_ajax_request:
                    if success:
                        # Include CSRF token in response for subsequent requests
                        csrf_token = None
                        if hasattr(form, 'csrf_token'):
                            csrf_token = form.csrf_token.current_token

                        return jsonify({
                            'success': True,
                            'message': f'Data sent to device {device_name}',
                            'timestamp': timestamp,
                            'csrf_token': csrf_token,
                            'data': {
                                'attributes': attributes,
                                'telemetry': telemetry
                            }
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'message': f'Error sending data: {error_msg}'
                        }), 500
                
                # For regular form submissions
                if success:
                    flash(f'Data sent to ThingsBoard device "{device_name}" successfully', 'success')
                else:
                    flash(f'Error sending data: {error_msg}', 'danger')
                
                # Return the generated data for display
                return render_template('generate_data.html', 
                                      profile=profile, 
                                      form=form, 
                                      attributes=attributes,
                                      telemetry=telemetry)
                                      
            except Exception as e:
                error_msg = str(e)
                print(f"ERROR: Exception in generate_data: {error_msg}")
                print(traceback.format_exc())
                
                if is_ajax_request:
                    return jsonify({
                        'success': False,
                        'message': f'Error: {error_msg}'
                    }), 500
                    
                flash(f'Error processing request: {error_msg}', 'danger')
        else:
            # Handle validation errors
            if is_ajax_request:
                errors = {field: ', '.join(errors) for field, errors in form.errors.items()}
                return jsonify({
                    'success': False,
                    'message': 'Validation error',
                    'errors': errors
                }), 400
            
            # Display errors in the form for regular submissions
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    # Initial form load or re-render after errors
    return render_template('generate_data.html', profile=profile, form=form)


def generate_random_value(attribute):
    attr_type = attribute['type']
    
    if attr_type == 'string' and attribute['options']:
        # Select random option from list
        return random.choice(attribute['options'])
    
    elif attr_type == 'number':
        min_val = float(attribute['min_value'] if attribute['min_value'] is not None else 0)
        max_val = float(attribute['max_value'] if attribute['max_value'] is not None else 100)
        
        # Generate random float
        value = random.uniform(min_val, max_val)
        
        # Round to 2 decimal places
        return round(value, 2)
    
    elif attr_type == 'integer':
        min_val = int(attribute['min_value'] if attribute['min_value'] is not None else 0)
        max_val = int(attribute['max_value'] if attribute['max_value'] is not None else 100)
        
        # Generate random integer
        return random.randint(min_val, max_val)
    
    elif attr_type == 'boolean':
        # Generate random boolean
        return random.choice([True, False])
    
    elif attr_type == 'string' and not attribute['options']:
        # Generate random string
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        length = random.randint(5, 10)
        return ''.join(random.choice(chars) for _ in range(length))
    
    # Default fallback
    return "N/A"


@main.route('/autonomous-generation', methods=['GET'])
def autonomous_generation_select():
    """
    Select device profiles for autonomous data generation.
    Displays a form where users can select one or more device profiles.
    """
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
    
    # Check if we have profiles
    if not profile_data:
        flash('Please create at least one device profile first', 'warning')
        return redirect(url_for('main.device_profiles'))
    
    return render_template('autonomous_select.html', profiles=profile_data)


@main.route('/autonomous-generation', methods=['POST'])
def autonomous_generation_configure():
    """
    Configure autonomous generation for selected profiles.
    Processes the selection and shows the configuration form.
    """
    if not tb_client or not tb_client.is_logged_in():
        flash('Please connect to ThingsBoard first', 'warning')
        return redirect(url_for('main.index'))
    
    # Get selected profiles
    selected_profile_names = request.form.getlist('selected_profiles')
    
    if not selected_profile_names:
        flash('Please select at least one device profile', 'warning')
        return redirect(url_for('main.autonomous_generation_select'))
    
    # Get the full profile data for selected profiles
    selected_profiles = []
    for name in selected_profile_names:
        for profile in profile_data:
            if profile['name'] == name:
                selected_profiles.append(profile)
                break
    
    form = AutonomousGenerationForm()
    
    # Convert selected profiles to JSON for JavaScript
    selected_profiles_json = json.dumps(selected_profiles)
    
    return render_template('autonomous_generate.html', 
                          form=form, 
                          selected_profiles=selected_profiles,
                          selected_profiles_json=selected_profiles_json)


@main.route('/api/autonomous-send-data', methods=['POST'])
def autonomous_send_data():
    """
    API endpoint for sending data in autonomous mode.
    Receives data via AJAX and sends it to ThingsBoard.
    """
    if not tb_client or not tb_client.is_logged_in():
        return jsonify({'success': False, 'error': 'Not connected to ThingsBoard'}), 401
    
    # Get data from request
    data = request.json
    
    try:
        profile_name = data.get('profile_name')
        device_name = data.get('device_name')
        device_data = data.get('data', {})
        data_type = data.get('data_type', 'telemetry')
        
        # Validate input
        if not profile_name or not device_name or not device_data:
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Get or create the device
        device = tb_client.get_or_create_device(device_name)
        device_id = device['id']
        
        timestamp = int(time.time() * 1000)  # Current time in milliseconds
        
        # Send data based on type
        if data_type == 'attributes':
            tb_client.send_attributes(device_id, device_data)
        else:  # telemetry
            tb_client.send_telemetry(device_id, device_data, timestamp)
        
        return jsonify({'success': True, 'message': f'Data sent to {device_name}'})
    
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@main.route('/device-profiles/autonomous', methods=['GET'])
def device_profile_autonomous():
    """
    Redirects to the autonomous generation page.
    """
    return redirect(url_for('main.autonomous_generation_select'))
