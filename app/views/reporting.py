# Python modules
from app.backend import pkg
from app.backend.influxdb.influxdb import influxdb
from app.backend.reporting.html.htmlreport import htmlReport
from app.backend.reporting.azurewiki.azureport import azureport

# Flask modules
from flask                   import render_template, request, url_for, redirect
from flask_login             import current_user

# App modules
from app         import app
from app.forms   import flowConfigForm, graphForm


@app.route('/flow', methods=['GET', 'POST'])
def flow():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    graphs = pkg.getGraphs(project)

    # Flask message injected into the page, in case of any errors
    msg = None

    # Declare the graphs form
    formForGraphs = graphForm(request.form)

    # Declare the Influxdb form
    form = flowConfigForm(request.form)
    form.influxdbName.choices = pkg.getInfluxdbConfigs(project)
    form.grafanaName.choices  = pkg.getGrafanaConfigs(project)
    form.azureName.choices    = pkg.getAzureConfigs(project)
    
    if form.validate_on_submit():
        msg = pkg.saveFlowConfig(project, request.form.to_dict())
    
    # get grafana parameter if provided
    flowConfig = None
    flowConfig = request.args.get('flowConfig')

    if flowConfig != None:
        output = pkg.getFlowConfigValuesInDict(project, flowConfig)
        print(output)
        form = flowConfigForm(output)
        form.influxdbName.choices = pkg.getInfluxdbConfigs(project)
        form.grafanaName.choices  = pkg.getGrafanaConfigs(project)
        form.azureName.choices    = pkg.getAzureConfigs(project)

    return render_template('home/flow.html', form = form, flowConfig = flowConfig, graphs = graphs, msg = msg, formForGraphs = formForGraphs)

@app.route('/delete/flow', methods=['GET'])
def deleteFlow():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # get azure parameter if provided
    flowConfig = None
    flowConfig = request.args.get('flowConfig')

    # Get current project
    project = request.cookies.get('project')  

    if flowConfig != None:
        pkg.deleteConfig(project, flowConfig)

    return redirect(url_for('integrations'))

@app.route('/all-flows', methods=['GET'])
def allFlows():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    flows = pkg.getFlowConfigs(project)
    return render_template('home/all-flows.html', flows = flows)

@app.route('/tests', methods=['GET'])
def getTests():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    influxdbObj = influxdb(project)
    influxdbObj.connectToInfluxDB()
    tests = influxdbObj.getTestLog()
    tests = pkg.sortTests(tests)

    return render_template('home/tests.html', tests=tests)

@app.route('/test-results', methods=['GET'])
def getTestResults():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  
    runId = request.args.get('runId')
    report = htmlReport(project, runId)
    report.createReport()
    return render_template('home/test-results.html', report=report.report)

@app.route('/generate-az-report', methods=['GET'])
def generateAzReport():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  
    runId = request.args.get('runId')
    baseline_runId = request.args.get('baseline_runId')
    reportName = request.args.get('reportName')

    azreport = azureport(project, reportName)
    azreport.generateReport(runId, baseline_runId)

    getTests()