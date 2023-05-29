# Python modules
from app.backend import pkg
from app.backend.integrations.influxdb.influxdb import influxdb
from app.backend.reporting.perforge_html import html_report
from app.backend.reporting.azure_wiki import azureport
from app.backend.reporting.atlassian_wiki import atlassian_wiki_report
from app.backend.reporting.atlassian_jira import atlassian_jira_report
from datetime import datetime

# Flask modules
from flask                   import render_template, request, url_for, redirect, flash
from flask_login             import current_user

# App modules
from app         import app
from app.forms   import flow_config_form, graph_form

import traceback


@app.route('/flow', methods=['GET', 'POST'])
def flow():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project = request.cookies.get('project')  
        graphs = pkg.get_config_names(project, "graphs")
        # Flask message injected into the page, in case of any errors
        msg = None
        # Declare the graphs form
        form_for_graphs = graph_form(request.form)
        # Declare the Influxdb form
        form = flow_config_form(request.form)
        form.influxdb.choices = pkg.get_integration_config_names(project, "influxdb")
        form.grafana.choices  = pkg.get_integration_config_names(project, "grafana")
        form.output.choices   = pkg.get_output_configs(project)
        # get grafana parameter if provided
        flow_config = request.args.get('flow_config')
        if flow_config != None:
            output = pkg.get_flow_config_values_in_dict(project, flow_config)
            form = flow_config_form(output)
            form.influxdb.choices = pkg.get_integration_config_names(project, "influxdb")
            form.grafana.choices  = pkg.get_integration_config_names(project, "grafana")
            form.output.choices   = pkg.get_output_configs(project)
        if form.validate_on_submit():
            msg = pkg.save_flow_config(project, request.form.to_dict())
            flash("Flow config added.")
            flow_config = request.form.to_dict()["name"]
        return render_template('home/flow.html', form = form, flow_config = flow_config, graphs = graphs, msg = msg, form_for_graphs = form_for_graphs)
    except Exception as er:
        flash("ERROR: " + str(er))
        return render_template('home/all-flows.html')

@app.route('/delete/flow', methods=['GET'])
def delete_flow():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # get azure parameter if provided
        flow_config = None
        flow_config = request.args.get('flow_config')
        # Get current project
        project = request.cookies.get('project')  
        if flow_config != None:
            pkg.delete_config(project, flow_config)
            flash("Flow config is deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return render_template('home/all-flows.html')

@app.route('/all-flows', methods=['GET'])
def all_flows():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project = request.cookies.get('project')  
        flows = pkg.get_config_names(project, "flow_configs")
        return render_template('home/all-flows.html', flows = flows)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for("index"))

@app.route('/tests', methods=['GET'])
def get_tests():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project = request.cookies.get('project')  
        influxdb_names = pkg.get_integration_config_names(project, "influxdb")
        influxdb_name = request.args.get('influxdb')
        influxdb_obj = influxdb(project=project, name=influxdb_name)
        influxdb_obj.connect_to_influxdb()
        msg = influxdb_obj.get_test_log()
        if(msg["status"] != "error"):
            tests = pkg.sort_tests(msg["message"])
        else:
            tests = []
        return render_template('home/tests.html', tests=tests, msg=msg, influxdb_names=influxdb_names)
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
        return redirect(url_for("index"))

@app.route('/report', methods=['GET'])
def get_report():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project = request.cookies.get('project')  
        runId = request.args.get('runId')
        influxdb_name = request.args.get('influxdb_name')
        report = html_report(project, runId, influxdb_name)
        report.create_report()
        return render_template('home/report.html', report=report.report)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for("index"))

@app.route('/generate-az-report', methods=['GET'])
def generate_azure_wiki_report():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project         = request.cookies.get('project')  
        runId           = request.args.get('runId')
        baseline_run_id = request.args.get('baseline_run_id')
        report_name     = request.args.get('report_name')
        azreport = azureport(project, report_name)
        azreport.generate_report(runId, baseline_run_id)
        return redirect(url_for('getTests'))
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for("index"))

@app.route('/generate-confl-report', methods=['GET'])
def generate_atlassian_wiki_report():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project         = request.cookies.get('project')  
        runId           = request.args.get('runId')
        baseline_run_id = request.args.get('baseline_run_id')
        report_name     = request.args.get('report_name')
        atlassian_wiki = atlassian_wiki_report(project, report_name)
        atlassian_wiki.generate_report(runId, baseline_run_id)
        return redirect(url_for('getTests'))
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for("index"))

@app.route('/generate-jira-report', methods=['GET'])
def generate_atlassian_jira_report():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
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