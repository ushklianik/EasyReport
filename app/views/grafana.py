# Flask modules
from flask import request, make_response

# App modules
from app                                        import app
from app.backend.reporting.azure_wiki           import azureport
from app.backend.integrations.influxdb.influxdb import influxdb
from app.backend.integrations.grafana.grafana   import grafana

# Route for generating Azure report
@app.route('/gen-az-report', methods=['GET'])
def gen_az_report():
    grafana_obj = grafana("default")
    # Get current project
    project         = "default"
    run_id          = request.args.get('run_id')
    baseline_run_id = request.args.get('baseline_run_id')
    report_name     = request.args.get('reportName')
    azreport        = azureport(project, report_name)
    azreport.generate_report(run_id, baseline_run_id)
    resp = make_response("Done")
    resp.headers['Access-Control-Allow-Origin'] = grafana_obj.server
    resp.headers['access-control-allow-methods'] = '*'
    resp.headers['access-control-allow-credentials'] = 'true'
    return resp

# Route for deleting InfluxDB data
@app.route('/delete-influxdata', methods=['GET'])
def influx_data_delete():
    influxdb_obj = influxdb("default")
    grafana_obj  = grafana("default")
    influxdb_obj.connect_to_influxdb()
    run_id = request.args.get('run_id')
    start  = request.args.get('start')
    end    = request.args.get('end')
    status = request.args.get('status')
    if request.args.get('user') == "admin":
        if status == "delete_test_status":
            influxdb_obj.delete_test_data("tests", run_id)
        elif status == "delete_test":
            influxdb_obj.delete_test_data(influxdb_obj.measurement, run_id)
            influxdb_obj.delete_test_data("tests", run_id)
            influxdb_obj.delete_test_data("virtualUsers", run_id)
            influxdb_obj.delete_test_data("testStartEnd", run_id)
        elif status == "delete_timerange":
            influxdb_obj.delete_test_data(influxdb_obj.measurement, run_id, start, end)
            influxdb_obj.delete_test_data("virtualUsers", run_id, start, end)
            influxdb_obj.delete_test_data("testStartEnd", run_id, start, end)
    resp = make_response("Done")
    resp.headers['Access-Control-Allow-Origin'] = grafana_obj.server
    resp.headers['access-control-allow-methods'] = '*'
    resp.headers['access-control-allow-credentials'] = 'true'
    return resp