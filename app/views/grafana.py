# Flask modules
from flask       import request, make_response
# App modules
from app         import app
from app.backend.reporting.azure_wiki import azureport
from app.backend.integrations.influxdb.influxdb import influxdb
from app.backend.integrations.grafana.grafana import grafana


@app.route('/gen-az-report', methods=['GET'])
def genAzReport():
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