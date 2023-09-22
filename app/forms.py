# -*- encoding: utf-8 -*-

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, IntegerField, PasswordField, FieldList, BooleanField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Email, DataRequired, NumberRange, Email


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    name     = StringField('Name')
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email    = StringField('Email', validators=[DataRequired(), Email()])


class InfluxDBForm(FlaskForm):
    name        = StringField('Name', validators=[DataRequired()])
    url         = StringField('Url', validators=[DataRequired()])
    org_id      = StringField('Org', validators=[DataRequired()])
    token       = StringField('Token', validators=[DataRequired()])
    timeout     = StringField('Timeout', validators=[DataRequired()])
    bucket      = StringField('Bucket', validators=[DataRequired()])
    listener    = SelectField('Backend listener', choices=[('org.apache.jmeter.visualizers.backend.influxdb.InfluxdbBackendListenerClient', 'org.apache.jmeter.visualizers.backend.influxdb.InfluxdbBackendListenerClient'), 
                                                           ('mderevyankoaqa', 'mderevyankoaqa')], default='InfluxdbBackendListenerClient')
    is_default  = SelectField('Default', choices=[('true', 'True'), ('false', 'False')], default='false')


class GrafanaForm(FlaskForm):
    name        = StringField('Name', validators=[DataRequired()])
    server      = StringField('Server', validators=[DataRequired()])
    token       = StringField('Token', validators=[DataRequired()])
    org_id      = StringField('OrgId', validators=[DataRequired()])
    dashboards  = FieldList(StringField('Dashboard'), min_entries=1)
    is_default  = SelectField('Default', choices=[('true', 'True'), ('false', 'False')], default='false')


class AzureForm(FlaskForm):
    name           = StringField('Name', validators=[DataRequired()])
    token          = StringField('Personal Access Token', validators=[DataRequired()])
    org_url        = StringField('Wiki Organization Url', validators=[DataRequired()])
    project_id     = StringField('Wiki Project', validators=[DataRequired()])
    identifier     = StringField('Wiki Identifier', validators=[DataRequired()])
    path_to_report = StringField('Wiki Path To Report', validators=[DataRequired()])
    is_default     = SelectField('Default', choices=[('true', 'True'), ('false', 'False')], default='false')


class TemplateConfigForm(FlaskForm):
    name     = StringField('Name', validators=[DataRequired()])
    graphs   = FieldList(StringField())
    footer   = TextAreaField('Footer')
    header   = TextAreaField('Header')
    flow     = SelectField('Flow name', validators=[DataRequired()])

class FlowConfigForm(FlaskForm):
    name     = StringField('Name', validators=[DataRequired()])
    influxdb = SelectField('Influxdb config', validators=[DataRequired()])
    grafana  = SelectField('Grafana config', validators=[DataRequired()])
    output   = SelectField('Output config', validators=[DataRequired()])


class GraphForm(FlaskForm):
    name       = StringField('Name', validators=[DataRequired()])
    view_panel = StringField('View panel id', validators=[DataRequired()])
    dash_id    = SelectField('Dashboard Id', validators=[DataRequired()])
    width      = StringField('Panel width', validators=[DataRequired()])
    height     = StringField('Panel height', validators=[DataRequired()])


class AtlassianWikiForm(FlaskForm):
    name       = StringField('Name', validators=[DataRequired()])
    token      = StringField('personalAccessToken', validators=[DataRequired()])
    org_url    = StringField('wikiOrganizationUrl', validators=[DataRequired()])
    parent_id  = StringField('wikiParentId', validators=[DataRequired()])
    space_key  = StringField('wikiSpaceKey', validators=[DataRequired()])
    username   = StringField('username', validators=[DataRequired()])
    is_default = SelectField('Default', choices=[('true', 'True'), ('false', 'False')], default='false')


class AtlassianJiraForm(FlaskForm):
    name       = StringField('Name', validators=[DataRequired()])
    email      = StringField('Email', validators=[DataRequired()])
    token      = StringField('Password', validators=[DataRequired()])
    org_url    = StringField('jiraOrganizationUrl', validators=[DataRequired()])
    project_id = StringField('Project', validators=[DataRequired()])
    epic_field = StringField('EpicField')
    epic_name  = StringField('EpicName')
    is_default = SelectField('Default', choices=[('true', 'True'), ('false', 'False')], default='false')

class SMTPMailForm(FlaskForm):
    name       = StringField('Name', validators=[DataRequired()])
    server     = StringField('Server', validators=[DataRequired()])
    port       = IntegerField('Port', validators=[DataRequired()])
    use_ssl    = SelectField('Use SSL', choices=[('True', 'True'), ('False', 'False')], default='True')
    use_tls    = SelectField('Use TLS', choices=[('True', 'True'), ('False', 'False')], default='False')
    username   = StringField('Username', validators=[DataRequired(), Email()])
    token      = StringField('Password', validators=[DataRequired()])
    recipients = FieldList(StringField('Recipient'), min_entries=1, validators=[DataRequired(), Email()])
    is_default = SelectField('Default', choices=[('true', 'True'), ('false', 'False')], default='false')