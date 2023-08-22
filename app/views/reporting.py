# Python modules
from datetime import datetime

from flask                   import render_template, request, url_for, redirect, flash, jsonify
from flask_login             import current_user

# App modules
from app                                        import app
from app.backend                                import pkg
from app.backend.integrations.influxdb.influxdb import influxdb
from app.backend.reporting.perforge_html        import html_report
from app.backend.reporting.azure_wiki           import azureport
from app.backend.reporting.atlassian_wiki       import atlassian_wiki_report
from app.backend.reporting.atlassian_jira       import atlassian_jira_report
from app.forms                                  import FlowConfigForm, TemplateConfigForm

import traceback
import json

# Route for managing flow configuration
@app.route('/template', methods=['GET', 'POST'])
def template():
    try:
        # Get current project
        project   = request.cookies.get('project')
        # Get graphs
        graphs    = pkg.get_config_names(project, "graphs")
        templates = pkg.get_config_names(project, "templates")
        flows     = pkg.get_config_names(project, "flows")
        # get grafana parameter if provided
        template  = request.args.get('template')
        template_data = []
        if template is not None:
            template_data = pkg.get_template_values(project, template)
        if request.method == "POST":
            pkg.save_template(project, request.get_json())
            flash("Template added.")
            return jsonify({'redirect_url': 'reporting'})
    except Exception:
        flash("ERROR: " + str(traceback.format_exc()))
        return redirect(url_for("get_reporting"))
    return render_template('home/template.html', graphs=graphs, templates=templates, flows=flows, template_data=template_data)

# Route for deleting flow configuration
@app.route('/delete-template', methods=['GET'])
def delete_template():
    try:
        template = request.args.get('template')
        # Get current project
        project = request.cookies.get('project')
        if template is not None:
            pkg.delete_config(project, template)
            flash("Template is deleted.")
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for("get_reporting"))

# Route for displaying all flow configurations
@app.route('/reporting', methods=['GET', 'POST'])
def get_reporting():
    try:
        # Get current project
        project               = request.cookies.get('project')
        flow                  = FlowConfigForm(request.form)
        flow.influxdb.choices = pkg.get_integration_config_names(project, "influxdb")
        flow.grafana.choices  = pkg.get_integration_config_names(project, "grafana")
        flow.output.choices   = pkg.get_output_configs(project)
        if flow.validate_on_submit():
            pkg.save_flow_config(project, request.form.to_dict())
            flash("Flow config added.")

        flows                 = pkg.get_config_names(project, "flows")
        templates             = pkg.get_config_names(project, "templates")
        return render_template('home/reporting.html', flows=flows, flow=flow, templates=templates)
    except Exception:
        flash("ERROR: " + str(traceback.format_exc()))
        return redirect(url_for("index"))
    
# Route for managing flow configuration
@app.route('/save-flow', methods=['GET', 'POST'])
def save_flow():
    try:
        # Get current project
        project = request.cookies.get('project')
        # Declare the Influxdb form
        form    = FlowConfigForm(request.form)
        if form.validate_on_submit():
            print(request.form.to_dict())
            pkg.save_flow_config(project, request.form.to_dict())
            flash("Flow config added.")
        return redirect(url_for("get_reporting"))
    except Exception:
        flash("ERROR: " + str(traceback.format_exc()))
        return redirect(url_for("get_reporting"))

# Route for deleting flow configuration
@app.route('/delete-flow', methods=['GET', 'POST'])
def delete_flow():
    try:
        flow = request.args.get('flow')
        # Get current project
        project = request.cookies.get('project')
        if flow is not None:
            pkg.delete_config(project, flow)
            flash("Flow is deleted.")
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for("get_reporting"))
    
@app.route('/tests', methods=['GET'])
def get_tests():
    # try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project = request.cookies.get('project')  
        influxdb_names = pkg.get_integration_config_names(project, "influxdb")
        templates = pkg.get_config_names(project, "templates")
        return render_template('home/tests.html', influxdb_names=influxdb_names, templates = templates)
    # except Exception as er:
    #     flash("ERROR: " + str(traceback.format_exc()))
    #     return redirect(url_for("index"))
    
@app.route('/load_tests', methods=['GET'])
def load_tests():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return jsonify(status="error", message="User not authenticated")
        # Get current project
        project = request.cookies.get('project')
        influxdb_name = request.args.get('influxdb_name')
        influxdb_obj = influxdb(project=project, name=influxdb_name)
        influxdb_obj.connect_to_influxdb()
        tests = influxdb_obj.get_test_log()
        if(tests):
            tests = pkg.sort_tests(tests)
        return jsonify(status="success", tests=tests)
    except Exception:
        flash("ERROR: " + str(traceback.format_exc()))
        return jsonify(status="error", message=str(traceback.format_exc()))

# Route for displaying HTML report
@app.route('/report', methods=['GET'])
def get_report():
    try:
        # Get current project
        project       = request.cookies.get('project')
        runId         = request.args.get('runId')
        influxdb_name = request.args.get('influxdb_name')
        report        = html_report(project, runId, influxdb_name)
        report.create_report()
        return render_template('home/report.html', report=report.report)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for("index"))

# Route for generating Azure wiki report
@app.route('/generate-az-report', methods=['GET'])
def generate_azure_wiki_report():
    try:
        # Get current project
        project         = request.cookies.get('project')
        runId           = request.args.get('runId')
        baseline_run_id = request.args.get('baseline_run_id')
        report_name     = request.args.get('report_name')
        azreport        = azureport(project, report_name)
        azreport.generate_report(runId, baseline_run_id)
        return redirect(url_for('getTests'))
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
        return redirect(url_for("index"))

# Route for generating Atlassian wiki report
@app.route('/generate-confl-report', methods=['GET'])
def generate_atlassian_wiki_report():
    try:
        # Get current project
        project         = request.cookies.get('project')
        runId           = request.args.get('runId')
        baseline_run_id = request.args.get('baseline_run_id')
        report_name     = request.args.get('report_name')
        atlassian_wiki  = atlassian_wiki_report(project, report_name)
        atlassian_wiki.generate_report(runId, baseline_run_id)
        return redirect(url_for('getTests'))
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for("index"))

# Route for generating Atlassian Jira report
@app.route('/generate-jira-report', methods=['GET'])
def generate_atlassian_jira_report():
    try:
        # Get current project
        project         = request.cookies.get('project')
        runId           = request.args.get('runId')
        baseline_run_id = request.args.get('baseline_run_id')
        report_name     = request.args.get('report_name')
        atlassian_jira  = atlassian_jira_report(project, report_name)
        atlassian_jira.generate_report(runId, baseline_run_id)
        return redirect(url_for('getTests'))
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for("index"))
    
# Route for generating a report
@app.route('/generate', methods=['GET','POST'])
def generate_report():
    # try:
        project       = request.cookies.get('project')
        if request.method == "POST":
            data      = request.get_json()
            template  = data["template"]
            action    = data["selectedAction"]
            result    = "Choose what you need"
            if action == "azure_report":
                az     = azureport(project, template)
                result = az.generate_report(data["tests"])
                del(az)
            elif action == "atlassian_wiki_report":
                awr    = atlassian_wiki_report(project, template)
                result = awr.generate_report(data["tests"])
                del(awr)
            return result
    # except Exception as er:
    #     flash("ERROR: " + str(er))
    #     return redirect(url_for("index"))

# Route for displaying Grafana result dashboard
@app.route('/grafana-result-dashboard', methods=['GET'])
def get_grafana_result_dashboard():
    try:
        # Get current project
        project               = request.cookies.get('project')
        runId                 = request.args.get('runId')
        testName              = request.args.get('testName')
        startTimestamp        = request.args.get('startTimestamp')
        endTimestamp          = request.args.get('endTimestamp')
        grafana_config        = pkg.get_default_grafana(project)
        grafana_config_values = pkg.get_grafana_config_values(project, grafana_config)
        return render_template('home/grafana-result-dashboard.html',
                               runId=runId,
                               testName=testName,
                               startTimestamp=startTimestamp,
                               endTimestamp=endTimestamp,
                               grafana_config_values=grafana_config_values)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for("index"))