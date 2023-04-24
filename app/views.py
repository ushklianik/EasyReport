# Python modules
from app.backend import pkg
# Flask modules
from flask       import render_template, request, url_for, redirect, make_response, send_from_directory, Response
# App modules
from app         import app
from app.forms   import flowConfigForm, graphForm, InfluxDBForm, grafanaForm, azureForm
from app.backend.validation.validation import nfr
from app.backend.reporting.azurewiki.azureport import azureport
from app.backend.influxdb.influxdb import influxdb
from app.backend.grafana.grafana import grafana
import os

app_dir = os.path.dirname(os.path.abspath(__file__))

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
    form.outputName.choices   = pkg.getOutputConfigs(project)
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
        form.outputName.choices   = pkg.getOutputConfigs(project)
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

@app.route('/', defaults={'path': 'index.html'})
def index(path):
    return render_template( 'home/' + path)

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
    grafanaObj = grafana("default")
    # Get current project
    project        = "default"
    runId          = request.args.get('runId')
    baseline_runId = request.args.get('baseline_runId')
    reportName     = request.args.get('reportName')
    azreport = azureport(project, reportName)
    azreport.generateReport(runId, baseline_runId)
    resp = make_response("Done")
    resp.headers['Access-Control-Allow-Origin'] = grafanaObj.grafanaServer
    resp.headers['access-control-allow-methods'] = '*'
    resp.headers['access-control-allow-credentials'] = 'true'
    return resp


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
            infludxObj.deleteTestData(measurement = "tests", runId = runId)
        elif status == "delete_test":
            infludxObj.deleteTestData(measurement = infludxObj.influxdbMeasurement, runId = runId)
            infludxObj.deleteTestData(measurement = "tests", runId = runId)
            infludxObj.deleteTestData(measurement = "virtualUsers", runId = runId)
            infludxObj.deleteTestData(measurement = "testStartEnd", runId = runId)
        elif status == "delete_timerange":
            infludxObj.deleteTestData(measurement = infludxObj.influxdbMeasurement, runId = runId, start = start, end = end)
            infludxObj.deleteTestData(measurement = "virtualUsers", runId = runId, start = start, end = end)
            infludxObj.deleteTestData(measurement = "testStartEnd", runId = runId, start = start, end = end)
            infludxObj.deleteTestData(measurement = "lighthouse", start = start, end = end)
            infludxObj.deleteTestData(measurement = "timingapi", start = start, end = end)
    resp = make_response("Done")
    resp.headers['Access-Control-Allow-Origin'] = grafanaObj.grafanaServer
    resp.headers['access-control-allow-methods'] = '*'
    resp.headers['access-control-allow-credentials'] = 'true'
    return resp

@app.route('/client-side', methods=['GET'])
def clientSide():
    reports = pkg.getHTMLReports(app_dir)
    return render_template('home/client-side.html', reports=reports)


@app.route('/reports/<path:path>')
def serve_report(path):
    full_path = os.path.join(app_dir, 'templates', 'reports', path)
    return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))

@app.route('/delete/report', methods=['GET'])
def deleteReport():
    report  = request.args.get('report')
    build  = request.args.get('build')
    pkg.deleteHTMLReport(app_dir, build, report)
    return redirect(url_for('clientSide'))