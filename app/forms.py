from flask_wtf          import FlaskForm
from wtforms            import StringField, FieldList, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired

class InfluxDBForm(FlaskForm):
	name                 = StringField  (u'Name'         , validators=[DataRequired()])
	influxdbUrl          = StringField  (u'Url'          , validators=[DataRequired()])
	influxdbOrg          = StringField  (u'Org'          , validators=[DataRequired()])
	influxdbToken        = StringField  (u'Token'        , validators=[DataRequired()])
	influxdbTimeout      = StringField  (u'Timeout'      , validators=[DataRequired()])
	influxdbBucket       = StringField  (u'Bucket'       , validators=[DataRequired()])
	influxdbMeasurement  = StringField  (u'Measurement'  , validators=[DataRequired()])
	influxdbField        = StringField  (u'Field'        , validators=[DataRequired()])
	influxdbTestIdTag    = StringField  (u'TestIdTag'    , validators=[DataRequired()])
	isDefault            = BooleanField()

class grafanaForm(FlaskForm):
	name                       = StringField  (u'Name'             , validators=[DataRequired()])
	grafanaServer              = StringField  (u'Server'           , validators=[DataRequired()])
	grafanaToken               = StringField  (u'Token'            , validators=[DataRequired()])
	grafanaDashboard           = StringField  (u'Dashboard'        , validators=[DataRequired()])
	grafanaOrgId               = StringField  (u'OrgId'            , validators=[DataRequired()])
	grafanaDashRenderPath      = StringField  (u'Render path'      , validators=[DataRequired()])
	grafanaDashRenderCompPath  = StringField  (u'Render path comp' , validators=[DataRequired()])
	isDefault                  = BooleanField()

class azureForm(FlaskForm):
	name                  = StringField  (u'Name'                    , validators=[DataRequired()])
	personalAccessToken   = StringField  (u'Personal Access Token'   , validators=[DataRequired()])
	wikiOrganizationUrl   = StringField  (u'Wiki Organization Url'   , validators=[DataRequired()])
	wikiProject           = StringField  (u'Wiki Project'            , validators=[DataRequired()])
	wikiIdentifier        = StringField  (u'Wiki Identifier'         , validators=[DataRequired()])
	wikiPathToReport      = StringField  (u'Wiki Path To Report'     , validators=[DataRequired()])
	appInsighsLogsServer  = StringField  (u'App Insighs Logs Server' , validators=[DataRequired()])
	appInsighsAppId       = StringField  (u'App Insighs App Id'      , validators=[DataRequired()])
	appInsighsApiKey      = StringField  (u'App Insighs Api Key'     , validators=[DataRequired()])
	isDefault             = BooleanField()

class flowConfigForm(FlaskForm):
	name                  = StringField         (u'Name'             , validators=[DataRequired()])
	graphs                = FieldList           (StringField()                                    )
	influxdbName          = SelectField         (u'Influxdb config'  , validators=[DataRequired()])
	grafanaName           = SelectField         (u'Grafana config'   , validators=[DataRequired()])
	outputName            = SelectField         (u'Output config'    , validators=[DataRequired()])
	footer                = TextAreaField       (u'Footer'                                        )
	header                = TextAreaField       (u'Header'                                        )

class graphForm(FlaskForm):
	name                  = StringField         (u'Name'             , validators=[DataRequired()])
	viewPanel             = StringField         (u'View panel id'    , validators=[DataRequired()])
	dashId                = StringField         (u'Dashboard Id'     , validators=[DataRequired()])
	fileName              = StringField         (u'File name'        , validators=[DataRequired()])
	width                 = StringField         (u'Panel width'      , validators=[DataRequired()])
	height                = StringField         (u'Panel height'     , validators=[DataRequired()])