# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, PasswordField, FieldList, BooleanField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Email, DataRequired

class login_form(FlaskForm):
	username      = StringField  (u'Username'  , validators=[DataRequired()])
	password      = PasswordField(u'Password'  , validators=[DataRequired()])

class register_form(FlaskForm):
	name          = StringField  (u'Name'      )
	username      = StringField  (u'Username'  , validators=[DataRequired()])
	password      = PasswordField(u'Password'  , validators=[DataRequired()])
	email         = StringField  (u'Email'     , validators=[DataRequired(), Email()])
	
class influxdb_form(FlaskForm):
	name         = StringField  (u'Name'         , validators=[DataRequired()])
	url          = StringField  (u'Url'          , validators=[DataRequired()])
	org_id       = StringField  (u'Org'          , validators=[DataRequired()])
	token        = StringField  (u'Token'        , validators=[DataRequired()])
	timeout      = StringField  (u'Timeout'      , validators=[DataRequired()])
	bucket       = StringField  (u'Bucket'       , validators=[DataRequired()])
	measurement  = StringField  (u'Measurement'  , validators=[DataRequired()])
	is_default   = SelectField  (u'Default', choices=[('true', 'True'), ('false', 'False')], default='false')

class grafana_form(FlaskForm):
	name                   = StringField  (u'Name'             , validators=[DataRequired()])
	server                 = StringField  (u'Server'           , validators=[DataRequired()])
	token                  = StringField  (u'Token'            , validators=[DataRequired()])
	dashboard_id           = StringField  (u'Dashboard'        , validators=[DataRequired()])
	org_id                 = StringField  (u'OrgId'            , validators=[DataRequired()])
	dash_render_path       = StringField  (u'Render path'      , validators=[DataRequired()])
	dash_render_comp_path  = StringField  (u'Render path comp' , validators=[DataRequired()])
	is_default             = SelectField  (u'Default', choices=[('true', 'True'), ('false', 'False')], default='false')

class azure_form(FlaskForm):
	name              = StringField  (u'Name'                    , validators=[DataRequired()])
	token             = StringField  (u'Personal Access Token'   , validators=[DataRequired()])
	org_url           = StringField  (u'Wiki Organization Url'   , validators=[DataRequired()])
	project_id        = StringField  (u'Wiki Project'            , validators=[DataRequired()])
	identifier        = StringField  (u'Wiki Identifier'         , validators=[DataRequired()])
	path_to_report    = StringField  (u'Wiki Path To Report'     , validators=[DataRequired()])
	is_default        = SelectField  (u'Default', choices=[('true', 'True'), ('false', 'False')], default='false')


class flow_config_form(FlaskForm):
	name              = StringField         (u'Name'             , validators=[DataRequired()])
	graphs            = FieldList           (StringField()                                    )
	influxdb          = SelectField         (u'Influxdb config'  , validators=[DataRequired()])
	grafana           = SelectField         (u'Grafana config'   , validators=[DataRequired()])
	output            = SelectField         (u'Output config'    , validators=[DataRequired()])
	footer            = TextAreaField       (u'Footer'                                        )
	header            = TextAreaField       (u'Header'                                        )

class graph_form(FlaskForm):
	name                  = StringField         (u'Name'             , validators=[DataRequired()])
	viewPanel             = StringField         (u'View panel id'    , validators=[DataRequired()])
	dashId                = StringField         (u'Dashboard Id'     , validators=[DataRequired()])
	fileName              = StringField         (u'File name'        , validators=[DataRequired()])
	width                 = StringField         (u'Panel width'      , validators=[DataRequired()])
	height                = StringField         (u'Panel height'     , validators=[DataRequired()])

class atlassian_wiki_form(FlaskForm):
	name               = StringField         (u'Name'                   , validators=[DataRequired()])
	token              = StringField         (u'personalAccessToken'    , validators=[DataRequired()])
	org_url            = StringField         (u'wikiOrganizationUrl'    , validators=[DataRequired()])
	parent_id          = StringField         (u'wikiParentId'           , validators=[DataRequired()])
	space_key          = StringField         (u'wikiSpaceKey'           , validators=[DataRequired()])
	username           = StringField         (u'username'               , validators=[DataRequired()])
	is_default         = SelectField  (u'Default', choices=[('true', 'True'), ('false', 'False')], default='false')

class atlassian_jira_form(FlaskForm):
	name                  = StringField         (u'Name'                   , validators=[DataRequired()])
	email                 = StringField         (u'Email'                  , validators=[DataRequired()])
	token                 = StringField         (u'Password'               , validators=[DataRequired()])
	org_url               = StringField         (u'jiraOrganizationUrl'    , validators=[DataRequired()])
	project_id            = StringField         (u'Project'                , validators=[DataRequired()])
	epic                  = StringField         (u'Epic'                                                )
	is_default            = SelectField  (u'Default', choices=[('true', 'True'), ('false', 'False')], default='false')