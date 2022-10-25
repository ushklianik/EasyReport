# Python modules
import os, logging 
from app.tools.tools import saveAzure, saveInfluxDB, getReports, getInfluxdbConfigs, getInfluxdbConfigValues, deleteInfluxdbConfig, getGrafanaConfigs, saveGrafana, getGrafnaConfigValues, deleteGrafana, getAzureConfigValues, deleteAzure, getAzureConfigs, getMetrics

# Flask modules
from flask                   import render_template, request, url_for, redirect, flash
from flask_login             import login_user, logout_user, current_user
from werkzeug.exceptions     import HTTPException, NotFound
from werkzeug.datastructures import MultiDict
from jinja2                  import TemplateNotFound

# App modules
from app         import app, lm, db, bc
from app.models  import Users
from app.forms   import LoginForm, RegisterForm, InfluxDBForm, grafanaForm, azureForm, reportForm

# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Logout user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    
    # declare the Registration Form
    form = RegisterForm(request.form)

    msg     = None
    success = False

    if request.method == 'GET': 

        return render_template( 'accounts/register.html', form=form, msg=msg )

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        email    = request.form.get('email'   , '', type=str) 

        # filter User out of database through username
        user = Users.query.filter_by(user=username).first()

        # filter User out of database through username
        user_by_email = Users.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'
        
        else:         

            pw_hash = bc.generate_password_hash(password)

            user = Users(username, email, pw_hash)

            user.save()

            msg     = 'User created, please <a href="' + url_for('login') + '">login</a>'     
            success = True

    else:
        msg = 'Input error'     

    return render_template( 'accounts/register.html', form=form, msg=msg, success=success )

# Authenticate user
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 

        # filter User out of database through username
        user = Users.query.filter_by(user=username).first()

        if user:
            
            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template( 'accounts/login.html', form=form, msg=msg )

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):
    
    reports = getReports()

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    try:
        
        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( 'home/' + path, reports = reports)
    
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    
    except:
        return render_template('home/page-500.html'), 500


@app.route('/integrations')
def integrations():
    influxdbConfigs = getInfluxdbConfigs()
    grafanaConfigs  = getGrafanaConfigs()
    azureConfigs = getAzureConfigs()
    return render_template('integrations/integrations.html', influxdbConfigs = influxdbConfigs, grafanaConfigs = grafanaConfigs, azureConfigs = azureConfigs)
    
@app.route('/influxdb', methods=['GET', 'POST'])
def addInfluxdb():

    # Declare the Influxdb form
    form = InfluxDBForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # get influxdb parameter if provided
    influxdbConfig = None
    influxdbConfig = request.args.get('influxdbConfig')

    if influxdbConfig != None:
        output = getInfluxdbConfigValues(influxdbConfig)
        form = InfluxDBForm(output)
                    
    if form.validate_on_submit():
        # assign form data to variables
        influxdbName        = request.form.get("influxdbName")
        influxdbUrl         = request.form.get("influxdbUrl")
        influxdbOrg         = request.form.get("influxdbOrg")
        influxdbToken       = request.form.get("influxdbToken")
        influxdbTimeout     = request.form.get("influxdbTimeout")
        influxdbBucket      = request.form.get("influxdbBucket")
        influxdbMeasurement = request.form.get("influxdbMeasurement")
        influxdbField       = request.form.get("influxdbField")
        msg = saveInfluxDB(influxdbName, influxdbUrl, influxdbOrg, influxdbToken, influxdbTimeout, influxdbBucket, influxdbMeasurement, influxdbField)

    return render_template('integrations/influxdb.html', form = form, msg = msg, influxdbConfig = influxdbConfig)

@app.route('/delete/influxdb', methods=['GET'])
def deleteInfluxdb():
    # get influxdb parameter if provided
    influxdbConfig = None
    influxdbConfig = request.args.get('influxdbConfig')

    if influxdbConfig != None:
        deleteInfluxdbConfig(influxdbConfig)

    return redirect(url_for('integrations'))


@app.route('/grafana', methods=['GET', 'POST'])
def addGrafana():

    # Declare the grafana form
    form = grafanaForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # get grafana parameter if provided
    grafanaConfig = None
    grafanaConfig = request.args.get('grafanaConfig')

    if grafanaConfig != None:
        output = getGrafnaConfigValues(grafanaConfig)
        form = grafanaForm(output)
                    
    if form.validate_on_submit():
        # assign form data to variables
        grafanaName               = request.form.get("grafanaName")
        grafanaServer             = request.form.get("grafanaServer")
        grafanaToken              = request.form.get("grafanaToken")
        grafanaDashboard          = request.form.get("grafanaDashboard")
        grafanaOrgId              = request.form.get("grafanaOrgId")
        grafanaDashRenderPath     = request.form.get("grafanaDashRenderPath")
        grafanaDashRenderCompPath = request.form.get("grafanaDashRenderCompPath")
        msg = saveGrafana( grafanaName, grafanaServer, grafanaToken, grafanaDashboard, grafanaOrgId, grafanaDashRenderPath, grafanaDashRenderCompPath )

    return render_template('integrations/grafana.html', form = form, msg = msg, grafanaConfig = grafanaConfig)


@app.route('/delete/grafana', methods=['GET'])
def deleteGrafanaConfig():
    # get grafana parameter if provided
    grafanaConfig = None
    grafanaConfig = request.args.get('grafanaConfig')

    if grafanaConfig != None:
        deleteGrafana(grafanaConfig)

    return redirect(url_for('integrations'))


@app.route('/azure', methods=['GET', 'POST'])
def addAzure():

    # Declare the azure form
    form = azureForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # get azure parameter if provided
    azureConfig = None
    azureConfig = request.args.get('azureConfig')

    if azureConfig != None:
        output = getAzureConfigValues(azureConfig)
        form = azureForm(output)
                    
    if form.validate_on_submit():
        # assign form data to variables
        azureName            = request.form.get("azureName")
        personalAccessToken  = request.form.get("personalAccessToken")
        wikiOrganizationUrl  = request.form.get("wikiOrganizationUrl")
        wikiProject          = request.form.get("wikiProject")
        wikiIdentifier       = request.form.get("wikiIdentifier")
        wikiPathToReport     = request.form.get("wikiPathToReport")
        appInsighsLogsServer = request.form.get("appInsighsLogsServer")
        appInsighsAppId      = request.form.get("appInsighsAppId")
        appInsighsApiKey     = request.form.get("appInsighsApiKey")
        msg = saveAzure( azureName, personalAccessToken, wikiOrganizationUrl, wikiProject, wikiIdentifier, wikiPathToReport, appInsighsLogsServer, appInsighsAppId, appInsighsApiKey )

    return render_template('integrations/azure.html', form = form, msg = msg, azureConfig = azureConfig)


@app.route('/delete/azure', methods=['GET'])
def deleteAzureConfig():
    # get azure parameter if provided
    azureConfig = None
    azureConfig = request.args.get('azureConfig')

    if azureConfig != None:
        deleteAzure(azureConfig)

    return redirect(url_for('integrations'))


@app.route('/report', methods=['GET', 'POST'])
def report():

    # Declare the Influxdb form
    form = reportForm(request.form)
    if request.method == "POST":
        print(request.form.listvalues)
    metrics = getMetrics()
    return render_template('home/report.html', form = form, metrics = metrics)