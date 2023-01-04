# Python modules
from app.backend import pkg
from app.backend.influxdb.main import influxdb
from app.backend.reporting.html.htmlreport import htmlReport

# Flask modules
from flask                   import render_template, request, url_for, redirect
from flask_login             import current_user

# App modules
from app         import app
from app.forms   import reportConfigForm, metricForm


@app.route('/report', methods=['GET', 'POST'])
def report():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    metrics = pkg.getMetrics(project)

    # Flask message injected into the page, in case of any errors
    msg = None

    # Declare the Metrics form
    formForMerics = metricForm(request.form)

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

    return render_template('home/report.html', form = form, reportConfig = reportConfig, metrics = metrics, msg = msg, formForMerics = formForMerics)

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


@app.route('/new-metric', methods=['POST'])
def newMetric():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    formForMerics = metricForm(request.form)
    # Get current project
    project = request.cookies.get('project')  

    if formForMerics.validate_on_submit():
        viewPanel      = request.form.get("viewPanel")
        dashId         = request.form.get("dashId")
        fileName       = request.form.get("fileName")
        width          = request.form.get("width")
        height         = request.form.get("height")
        msg = pkg.saveMetric(project, viewPanel, dashId, fileName, width, height)

    return render_template('home/all-reports.html')


@app.route('/set-project', methods=['GET'])
def setProject():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.args.get('project')
    # If project not provided, the default value is selected
    if project == None:
        project = "default"

    res = redirect(url_for('index'))
    res.set_cookie(key = 'project', value = project, max_age=None)
    return res

@app.route('/get-projects', methods=['GET'])
def getProjects():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get all projects
    projects = pkg.getProjects()
    return {'projects': projects}

@app.route('/tests', methods=['GET'])
def getTests():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    tests = influxdb(project).getTestLog()
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