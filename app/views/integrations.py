

# Flask modules
from flask                   import render_template, request, url_for, redirect
from flask_login             import current_user

# App modules
from app         import app
from app.forms   import InfluxDBForm, grafanaForm, azureForm
from app.backend import pkg


@app.route('/integrations')
def integrations():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    # Get integrations configs
    influxdbConfigs = pkg.getInfluxdbConfigs(project)
    grafanaConfigs  = pkg.getGrafanaConfigs(project)
    azureConfigs    = pkg.getAzureConfigs(project)

    return render_template('integrations/integrations.html', influxdbConfigs = influxdbConfigs, grafanaConfigs = grafanaConfigs, azureConfigs = azureConfigs)
    
@app.route('/influxdb', methods=['GET', 'POST'])
def addInfluxdb():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Declare the Influxdb form
    form = InfluxDBForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # get influxdb parameter if provided
    influxdbConfig = None
    influxdbConfig = request.args.get('influxdbConfig')

    # Get current project
    project = request.cookies.get('project')  

    if influxdbConfig != None:
        output = pkg.getInfluxdbConfigValues(project, influxdbConfig)
        form = InfluxDBForm(output)
                    
    if form.validate_on_submit():
        # 
        msg = pkg.saveInfluxDB(project, request.form.to_dict())

    return render_template('integrations/influxdb.html', form = form, msg = msg, influxdbConfig = influxdbConfig)

@app.route('/delete/influxdb', methods=['GET'])
def deleteInfluxdb():
    # # Check if user is logged in
    # if not current_user.is_authenticated:
    #     return redirect(url_for('login'))

    # get influxdb parameter if provided
    influxdbConfig = None
    influxdbConfig = request.args.get('influxdbConfig')

    # Get current project
    project = request.cookies.get('project')  

    if influxdbConfig != None:
        pkg.deleteConfig(project, influxdbConfig)

    return redirect(url_for('integrations'))


@app.route('/grafana', methods=['GET', 'POST'])
def addGrafana():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Declare the grafana form
    form = grafanaForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # Get current project
    project = request.cookies.get('project')  

    # get grafana parameter if provided
    grafanaConfig = None
    grafanaConfig = request.args.get('grafanaConfig')

    if grafanaConfig != None:
        output = pkg.getGrafnaConfigValues(project, grafanaConfig)
        form = grafanaForm(output)
                    
    if form.validate_on_submit():
        # assign form data to variables
        msg = pkg.saveGrafana( project, request.form.to_dict() )

    return render_template('integrations/grafana.html', form = form, msg = msg, grafanaConfig = grafanaConfig)


@app.route('/delete/grafana', methods=['GET'])
def deleteGrafanaConfig():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # get grafana parameter if provided
    grafanaConfig = None
    grafanaConfig = request.args.get('grafanaConfig')

    # Get current project
    project = request.cookies.get('project')  

    if grafanaConfig != None:
        pkg.deleteConfig(project, grafanaConfig)

    return redirect(url_for('integrations'))


@app.route('/azure', methods=['GET', 'POST'])
def addAzure():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Declare the azure form
    form = azureForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # Get current project
    project = request.cookies.get('project')  

    # get azure parameter if provided
    azureConfig = None
    azureConfig = request.args.get('azureConfig')

    if azureConfig != None:
        output = pkg.getAzureConfigValues(project, azureConfig)
        form = azureForm(output)
                    
    if form.validate_on_submit():
        # assign form data to variables
        msg = pkg.saveAzure( project, request.form.to_dict() )

    return render_template('integrations/azure.html', form = form, msg = msg, azureConfig = azureConfig)


@app.route('/delete/azure', methods=['GET'])
def deleteAzureConfig():

    # get azure parameter if provided
    azureConfig = None
    azureConfig = request.args.get('azureConfig')

    # Get current project
    project = request.cookies.get('project')  

    if azureConfig != None:
        pkg.deleteConfig(project, azureConfig)

    return redirect(url_for('integrations'))