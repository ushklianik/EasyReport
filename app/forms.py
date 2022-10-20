# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, TextAreaField, SubmitField, PasswordField
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


