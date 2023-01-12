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
from app.forms   import reportConfigForm, graphForm


@app.route('/report', methods=['GET', 'POST'])
def report():

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
    form = reportConfigForm(request.form)
    form.influxdbName.choices = pkg.getInfluxdbConfigs(project)
    form.grafanaName.choices  = pkg.getGrafanaConfigs(project)
    form.azureName.choices    = pkg.getAzureConfigs(project)
    
    if form.validate_on_submit():
        msg = pkg.saveReportConfig(project, request.form.to_dict())
    
    # get grafana parameter if provided
    reportConfig = None
    reportConfig = request.args.get('reportConfig')

    if reportConfig != None:
        output = pkg.getReportConfigValuesInDict(project, reportConfig)
        print(output)
        form = reportConfigForm(output)
        form.influxdbName.choices = pkg.getInfluxdbConfigs(project)
        form.grafanaName.choices  = pkg.getGrafanaConfigs(project)
        form.azureName.choices    = pkg.getAzureConfigs(project)

    return render_template('home/report.html', form = form, reportConfig = reportConfig, graphs = graphs, msg = msg, formForGraphs = formForGraphs)

@app.route('/delete/report', methods=['GET'])
def deleteReportConfig():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # get azure parameter if provided
    reportConfig = None
    reportConfig = request.args.get('reportConfig')

    # Get current project
    project = request.cookies.get('project')  

    if reportConfig != None:
        pkg.deleteConfig(project, reportConfig)

    return redirect(url_for('integrations'))

@app.route('/all-reports', methods=['GET'])
def allReports():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    reports = pkg.getReportConfigs(project)
    return render_template('home/all-reports.html', reports = reports)

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

@app.route('/report-flow', methods=['GET'])
def proceedWithFlow():

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