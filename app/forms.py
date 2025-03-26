from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, FloatField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, ValidationError


class ConnectionForm(FlaskForm):
    """Form for connecting to ThingsBoard"""
    host = StringField('ThingsBoard Host', validators=[DataRequired()])
    port = StringField('Port', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Connect')


class DeviceProfileForm(FlaskForm):
    """Form for creating a device profile"""
    name = StringField('Profile Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Create Profile')


class AttributeForm(FlaskForm):
    """Form for adding an attribute, telemetry or metadata to a device profile"""
    name = StringField('Attribute Name', validators=[DataRequired(), Length(min=1, max=50)])
    data_category = SelectField('Data Category',
                         choices=[
                             ('telemetry', 'Telemetry'),
                             ('attributes', 'Attributes'),
                             ('metadata', 'Metadata')
                         ],
                         default='telemetry',
                         validators=[DataRequired()])
    data_type = SelectField('Data Type', 
                          choices=[
                              ('number', 'Number (Float)'),
                              ('integer', 'Integer'),
                              ('string', 'String'),
                              ('boolean', 'Boolean')
                          ],
                          validators=[DataRequired()])
    min_value = FloatField('Minimum Value', validators=[Optional()])
    max_value = FloatField('Maximum Value', validators=[Optional()])
    default_value = StringField('Default Value', validators=[Optional()])
    options = StringField('Options (comma separated, for string type)', validators=[Optional()])
    persist = BooleanField('Persist Value', default=True)
    submit = SubmitField('Add Item')


class GenerateDataForm(FlaskForm):
    """Form for generating data for a device"""
    device_name = StringField('Device Name', validators=[DataRequired(), Length(min=2, max=50)])
    data_type = SelectField('Data Type', 
                          choices=[
                              ('telemetry', 'Telemetry'),
                              ('attributes', 'Attributes')
                          ],
                          validators=[DataRequired()])
    include_attributes = BooleanField('Include Attributes', default=True)
    include_metadata = BooleanField('Include Metadata', default=False)
    submit = SubmitField('Generate & Send Data')


class AutonomousGenerationForm(FlaskForm):
    """Form for autonomous data generation"""
    # Device Configuration
    generate_device_names = BooleanField('Generate Random Device Names')
    device_name_prefix = StringField('Device Name Prefix', default='TBDG_')
    
    # Timing Configuration
    interval_value = IntegerField('Interval Value', validators=[DataRequired(), NumberRange(min=1)], default=10)
    interval_unit = SelectField('Interval Unit', 
                         choices=[
                             ('seconds', 'Seconds'),
                             ('minutes', 'Minutes'),
                             ('hours', 'Hours')
                         ],
                         default='seconds',
                         validators=[DataRequired()])
    
    # Data Configuration
    data_type = SelectField('Data Type', 
                          choices=[
                              ('telemetry', 'Telemetry'),
                              ('attributes', 'Attributes')
                          ],
                          default='telemetry',
                          validators=[DataRequired()])
    
    include_attributes = BooleanField('Include Attributes', default=True)
    include_metadata = BooleanField('Include Metadata', default=False)
    
    submit = SubmitField('Configure Devices')
