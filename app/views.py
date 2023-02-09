# Python modules
from app.backend import pkg
# Flask modules
from flask       import render_template, request, url_for, redirect, make_response
# App modules
from app         import app
from app.forms   import flowConfigForm, graphForm, InfluxDBForm, grafanaForm, azureForm
from app.backend.validation.validation import nfr
from app.backend.reporting.azurewiki.azureport import azureport
from app.backend.influxdb.influxdb import influxdb
from app.backend.grafana.grafana import grafana



@app.route('/flow', methods=['GET', 'POST'])
def flow():
    project = "default"
    graphs = pkg.getGraphs(project)
    # Flask message injected into the page, in case of any errors
    msg = None
    # Declare the graphs form
    formForGraphs = graphForm(request.form)
    # Declare the Influxdb form
    form = flowConfigForm(request.form)
    form.influxdbName.choices = pkg.getInfluxdbConfigs(project)
    form.grafanaName.choices  = pkg.getGrafanaConfigs(project)
    form.outputName.choices   = pkg.getInfluxdbConfigs(project)
    if form.validate_on_submit():
        msg = pkg.saveFlowConfig(project, request.form.to_dict())
    # get grafana parameter if provided
    flowConfig = None
    flowConfig = request.args.get('flowConfig')
    if flowConfig != None:
        output = pkg.getFlowConfigValuesInDict(project, flowConfig)
        form = flowConfigForm(output)
        form.influxdbName.choices = pkg.getInfluxdbConfigs(project)
        form.grafanaName.choices  = pkg.getGrafanaConfigs(project)
        form.outputName.choices   = pkg.getInfluxdbConfigs(project)
    return render_template('home/flow.html', form = form, flowConfig = flowConfig, graphs = graphs, msg = msg, formForGraphs = formForGraphs)

@app.route('/delete/flow', methods=['GET'])
def deleteFlow():
    # get azure parameter if provided
    flowConfig = None
    flowConfig = request.args.get('flowConfig')
    project = "default"
    if flowConfig != None:
        pkg.deleteConfig(project, flowConfig)
    return redirect(url_for('integrations'))

@app.route('/all-flows', methods=['GET'])
def allFlows():
    project = "default"
    flows = pkg.getFlowConfigs(project)
    return render_template('home/all-flows.html', flows = flows)


@app.route('/', methods=['GET'])
def index():
    return render_template( 'home/index.html')


@app.route('/new-graph', methods=['POST'])
def newGraph():
    msg = None
    project = "default"
    if request.method == "POST":
        msg = pkg.saveGraph(project, request.get_json())
        print(request.get_json())
    return msg


@app.route('/integrations')
def integrations():
    project = "default"
    # Get integrations configs
    influxdbConfigs  = pkg.getInfluxdbConfigs(project)
    grafanaConfigs   = pkg.getGrafanaConfigs(project)
    azureConfigs     = pkg.getAzureConfigs(project)
    return render_template('integrations/integrations.html', 
                           influxdbConfigs  = influxdbConfigs, 
                           grafanaConfigs   = grafanaConfigs, 
                           azureConfigs     = azureConfigs)
    
@app.route('/influxdb', methods=['GET', 'POST'])
def addInfluxdb():
    # Declare the Influxdb form
    form = InfluxDBForm(request.form)
    # Flask message injected into the page, in case of any errors
    msg = None
    # get influxdb parameter if provided
    influxdbConfig = None
    influxdbConfig = request.args.get('influxdbConfig')
    project = "default"
    if influxdbConfig != None:
        output = pkg.getInfluxdbConfigValues(project, influxdbConfig)
        form = InfluxDBForm(output)                 
    if form.validate_on_submit():
        msg = pkg.saveInfluxDB(project, request.form.to_dict())
    return render_template('integrations/influxdb.html', form = form, msg = msg, influxdbConfig = influxdbConfig)

@app.route('/delete/influxdb', methods=['GET'])
def deleteInfluxdb():
    # get influxdb parameter if provided
    influxdbConfig = None
    influxdbConfig = request.args.get('influxdbConfig')
    project = "default"
    if influxdbConfig != None:
        pkg.deleteConfig(project, influxdbConfig)
    return redirect(url_for('integrations'))


@app.route('/grafana', methods=['GET', 'POST'])
def addGrafana():
    # Declare the grafana form
    form = grafanaForm(request.form)
    # Flask message injected into the page, in case of any errors
    msg = None
    project = "default"
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
    # get grafana parameter if provided
    grafanaConfig = None
    grafanaConfig = request.args.get('grafanaConfig')
    project = "default"
    if grafanaConfig != None:
        pkg.deleteConfig(project, grafanaConfig)
    return redirect(url_for('integrations'))


@app.route('/azure', methods=['GET', 'POST'])
def addAzure():
    # Declare the azure form
    form = azureForm(request.form)
    # Flask message injected into the page, in case of any errors
    msg = None
    project = "default"
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
    project = "default"
    if azureConfig != None:
        pkg.deleteConfig(project, azureConfig)
    return redirect(url_for('integrations'))


@app.route('/nfrs', methods=['GET'])
def getNFRs():
    project = "default"
    nfrObject = nfr(project)
    nfrsList = nfrObject.getNFRs()
    return render_template('home/nfrs.html', nfrsList=nfrsList)

@app.route('/nfr', methods=['GET', 'POST'])
def getNFR(): 
    nfrs = {}
    project = "default"
    if request.method == "POST":
        nfrObject = nfr(project)
        nfrObject.saveNFRs(request.get_json())
    if request.args.get('appName') != None:
        nfrObject = nfr(project)
        nfrs = nfrObject.getNFR(request.args.get('appName'))
    return render_template('home/nfr.html', nfrs=nfrs)

@app.route('/delete-nfr', methods=['GET'])
def deleteNFR():
    nfrs = {}
    project = "default"
    if request.args.get('appName') != None:
        nfrObject = nfr(project)
        nfrs = nfrObject.deleteNFR(request.args.get('appName'))
    return render_template('home/nfrs.html', nfrs=nfrs)

@app.route('/generate-az-report', methods=['GET'])
def generateAzReport():
    # Get current project
    project        = "default"
    runId          = request.args.get('runId')
    baseline_runId = request.args.get('baseline_runId')
    reportName     = request.args.get('reportName')
    azreport = azureport(project, reportName)
    azreport.generateReport(runId, baseline_runId)
    return redirect(url_for('index'))


@app.route('/set-baseline', methods=['GET'])
def setBaseline():
    infludxObj = influxdb("default")
    grafanaObj = grafana("default")
    infludxObj.connectToInfluxDB()
    if request.args.get('user') == "admin":
        infludxObj.addOrUpdateTest(runId = request.args.get('runId'),status = request.args.get('status'), build = request.args.get('build'), testName = request.args.get('testName'))
    resp = make_response("Done")
    resp.headers['Access-Control-Allow-Origin'] = grafanaObj.grafanaServer
    resp.headers['access-control-allow-methods'] = '*'
    resp.headers['access-control-allow-credentials'] = 'true'
    infludxObj.closeInfluxdbConnection()
    return resp

@app.route('/delete-influxdata', methods=['GET'])
def influxDataDelete():
    infludxObj = influxdb("default")
    grafanaObj = grafana("default")
    infludxObj.connectToInfluxDB()
    runId  = request.args.get('runId')
    start  = request.args.get('start')
    end    = request.args.get('end')
    status = request.args.get('status')
    if request.args.get('user') == "admin":
        if status == "delete_test_status":
            infludxObj.deleteTestData("tests", runId)
        elif status == "delete_test":
            infludxObj.deleteTestData(infludxObj.influxdbMeasurement, runId)
            infludxObj.deleteTestData("tests", runId)
            infludxObj.deleteTestData("virtualUsers", runId)
            infludxObj.deleteTestData("testStartEnd", runId)
        elif status == "delete_timerange":
            infludxObj.deleteTestData(infludxObj.influxdbMeasurement, runId, start, end)
            infludxObj.deleteTestData("virtualUsers", runId, start, end)
            infludxObj.deleteTestData("testStartEnd", runId, start, end)
    resp = make_response("Done")
    resp.headers['Access-Control-Allow-Origin'] = grafanaObj.grafanaServer
    resp.headers['access-control-allow-methods'] = '*'
    resp.headers['access-control-allow-credentials'] = 'true'
    return resp