# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, TextAreaField, SubmitField, PasswordField, SelectMultipleField, FieldList, FormField
from wtforms.validators import InputRequired, Email, DataRequired

class LoginForm(FlaskForm):
	username      = StringField  (u'Username'  , validators=[DataRequired()])
	password      = PasswordField(u'Password'  , validators=[DataRequired()])

class RegisterForm(FlaskForm):
	name          = StringField  (u'Name'      )
	username      = StringField  (u'Username'  , validators=[DataRequired()])
	password      = PasswordField(u'Password'  , validators=[DataRequired()])
	email         = StringField  (u'Email'     , validators=[DataRequired(), Email()])

class InfluxDBForm(FlaskForm):
	influxdbName         = StringField  (u'Name'         , validators=[DataRequired()])
	influxdbUrl          = StringField  (u'Url'          , validators=[DataRequired()])
	influxdbOrg          = StringField  (u'Org'          , validators=[DataRequired()])
	influxdbToken        = StringField  (u'Token'        , validators=[DataRequired()])
	influxdbTimeout      = StringField  (u'Timeout'      , validators=[DataRequired()])
	influxdbBucket       = StringField  (u'Bucket'       , validators=[DataRequired()])
	influxdbMeasurement  = StringField  (u'Measurement'  , validators=[DataRequired()])
	influxdbField        = StringField  (u'Field'        , validators=[DataRequired()])

class grafanaForm(FlaskForm):
	grafanaName                = StringField  (u'Name'             , validators=[DataRequired()])
	grafanaServer              = StringField  (u'Server'           , validators=[DataRequired()])
	grafanaToken               = StringField  (u'Token'            , validators=[DataRequired()])
	grafanaDashboard           = StringField  (u'Dashboard'        , validators=[DataRequired()])
	grafanaOrgId               = StringField  (u'OrgId'            , validators=[DataRequired()])
	grafanaDashRenderPath      = StringField  (u'Render path'      , validators=[DataRequired()])
	grafanaDashRenderCompPath  = StringField  (u'Render path comp' , validators=[DataRequired()])

class azureForm(FlaskForm):
	azureName             = StringField  (u'Name'                    , validators=[DataRequired()])
	personalAccessToken   = StringField  (u'Personal Access Token'   , validators=[DataRequired()])
	wikiOrganizationUrl   = StringField  (u'Wiki Organization Url'   , validators=[DataRequired()])
	wikiProject           = StringField  (u'Wiki Project'            , validators=[DataRequired()])
	wikiIdentifier        = StringField  (u'Wiki Identifier'         , validators=[DataRequired()])
	wikiPathToReport      = StringField  (u'Wiki Path To Report'     , validators=[DataRequired()])
	appInsighsLogsServer  = StringField  (u'App Insighs Logs Server' , validators=[DataRequired()])
	appInsighsAppId       = StringField  (u'App Insighs App Id'      , validators=[DataRequired()])
	appInsighsApiKey      = StringField  (u'App Insighs Api Key'     , validators=[DataRequired()])

class reportForm(FlaskForm):
	reportName            = StringField         (u'Name'             , validators=[DataRequired()])
	metrics               = FieldList           (StringField()                                    )
	influxdbName          = SelectMultipleField (u'Influxdb config'  , validators=[DataRequired()])
	grafanaName           = SelectMultipleField (u'Grafana config'   , validators=[DataRequired()])
	azureName             = SelectMultipleField (u'Azure config'     , validators=[DataRequired()])
