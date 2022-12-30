# Python modules
from app.backend import tools
from app.backend.influxdb.main import influxdb
from app.backend.reporting.htmlreport import htmlReport

# Flask modules
from flask                   import render_template, request, url_for, redirect
from flask_login             import current_user

# App modules
from app         import app
from app.forms   import reportForm, metricForm


@app.route('/report', methods=['GET', 'POST'])
def report():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    metrics = tools.getMetrics(project)

    # Flask message injected into the page, in case of any errors
    msg = None

    # Declare the Metrics form
    formForMerics = metricForm(request.form)

    # Declare the Influxdb form
    form = reportForm(request.form)
    form.influxdbName.choices = tools.getInfluxdbConfigs(project)
    form.grafanaName.choices  = tools.getGrafanaConfigs(project)
    form.azureName.choices    = tools.getAzureConfigs(project)
    
    if form.validate_on_submit():
        msg = tools.saveReport(project, request.form.to_dict())
    
    # get grafana parameter if provided
    reportConfig = None
    reportConfig = request.args.get('reportConfig')

    if reportConfig != None:
        output = tools.getReportConfigValues(project, reportConfig)
        form = reportForm(output)

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
        tools.deleteReport(project, reportConfig)

    return redirect(url_for('integrations'))

@app.route('/all-reports', methods=['GET'])
def allReports():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    reports = tools.getReports(project)
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
        msg = tools.saveMetric(project, viewPanel, dashId, fileName, width, height)

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
    projects = tools.getProjects()
    return {'projects': projects}

@app.route('/tests', methods=['GET'])
def getTests():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  

    tests = influxdb(project).getTestLog()
    tests = tools.sortTests(tests)

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