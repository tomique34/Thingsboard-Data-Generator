from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


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
    """Form for adding an attribute to a device profile"""
    name = StringField('Attribute Name', validators=[DataRequired(), Length(min=1, max=50)])
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
    options = StringField('Options (comma separated, for string type)', validators=[Optional()])
    submit = SubmitField('Add Attribute')


class GenerateDataForm(FlaskForm):
    """Form for generating data for a device"""
    device_name = StringField('Device Name', validators=[DataRequired(), Length(min=2, max=50)])
    data_type = SelectField('Data Type', 
                          choices=[
                              ('telemetry', 'Telemetry'),
                              ('attributes', 'Attributes')
                          ],
                          validators=[DataRequired()])
    submit = SubmitField('Generate & Send Data')
