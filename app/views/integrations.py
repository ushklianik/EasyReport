

# Flask modules
from flask                   import render_template, request, url_for, redirect, flash
from flask_login             import current_user

# App modules
from app         import app
from app.forms   import InfluxDBForm, GrafanaForm, AzureForm, AtlassianWikiForm, AtlassianJiraForm
from app.backend import pkg
import traceback


@app.route('/integrations')
def integrations():
    try:
        # Get current project
        project = request.cookies.get('project')  
        # Get integrations configs
        influxdb_configs  = pkg.get_integration_config_names(project, "influxdb")
        grafana_configs   = pkg.get_integration_config_names(project, "grafana")
        azure_configs     = pkg.get_integration_config_names(project, "azure")
        atlassian_wiki_configs = pkg.get_integration_config_names(project, "atlassian_wiki")
        atlassian_jira_configs = pkg.get_integration_config_names(project, "atlassian_jira")
        return render_template('home/integrations.html', 
                           influxdb_configs       = influxdb_configs, 
                           grafana_configs        = grafana_configs, 
                           azure_configs          = azure_configs, 
                           atlassian_wiki_configs = atlassian_wiki_configs,
                           atlassian_jira_configs = atlassian_jira_configs
                           )
    except Exception as er:
        flash("ERROR: " + str(er))
        return render_template('home/integrations.html')
    
@app.route('/influxdb', methods=['GET', 'POST'])
def add_influxdb():
    try:
        # Declare the Influxdb form
        form = InfluxDBForm(request.form)
        # get influxdb parameter if provided
        influxdb_config = request.args.get('influxdb_config')
        # Get current project
        project = request.cookies.get('project')  
        if influxdb_config != None:
            output = pkg.get_influxdb_config_values(project, influxdb_config)
            form = InfluxDBForm(output)               
        if form.validate_on_submit():
            pkg.save_influxdb(project, request.form.to_dict())
            influxdb_config = request.form.to_dict()["name"]
            flash("Integration added.")
        return render_template('integrations/influxdb.html', form = form, influxdb_config = influxdb_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))

@app.route('/delete/influxdb', methods=['GET'])
def delete_influxdb():
    try:
        # get influxdb parameter if provided
        influxdb_config = request.args.get('influxdb_config')
        # Get current project
        project = request.cookies.get('project')  
        if influxdb_config != None:
            pkg.delete_config(project, influxdb_config)
            flash("Integration deleted.")
    except Exception:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for('integrations'))


@app.route('/grafana', methods=['GET', 'POST'])
def add_grafana():
    try:
        # Get current project
        project = request.cookies.get('project')  
        # get grafana parameter if provided
        grafana_config = request.args.get('grafana_config')
        if request.method == 'POST':
            pkg.save_grafana( project, request.get_json())
            grafana_config = request.get_json()["name"]
            flash("Integration added.")
            return "grafana_config="+grafana_config
        return render_template('integrations/grafana.html', grafana_config = grafana_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))

@app.route('/grafana-config', methods=['GET'])
def get_grafana_config():
    try:
        output = "no data"
        # Get current project
        project = request.cookies.get('project')  
        # get grafana parameter if provided
        grafana_config = request.args.get('grafana_config')
        if grafana_config != None:
            output = pkg.get_grafana_config_values(project, grafana_config)
            print(output)
        return output
    except Exception as er:
        flash("ERROR: " + str(er))


@app.route('/delete/grafana', methods=['GET'])
def delete_grafana_config():
    try:
        # get grafana parameter if provided
        grafana_config = request.args.get('grafana_config')
        # Get current project
        project = request.cookies.get('project')  
        if grafana_config != None:
            pkg.delete_config(project, grafana_config)
            flash("Integration deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('integrations'))


@app.route('/azure', methods=['GET', 'POST'])
def add_azure():
    try:
        # Declare the azure form
        form = AzureForm(request.form)
        # Get current project
        project = request.cookies.get('project')  
        # get azure parameter if provided
        azure_config = request.args.get('azure_config')
        if azure_config != None:
            output = pkg.get_azure_config_values(project, azure_config)
            form = AzureForm(output)             
        if form.validate_on_submit():
            # assign form data to variables
            pkg.save_azure( project, request.form.to_dict())
            azure_config = request.form.to_dict()["name"]
            flash("Integration added.")
        return render_template('integrations/azure.html', form = form, azure_config = azure_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))


@app.route('/delete/azure', methods=['GET'])
def delete_azure_config():
    try:
        # get azure parameter if provided
        azure_config = None
        azure_config = request.args.get('azure_config')
        # Get current project
        project = request.cookies.get('project')  
        if azure_config != None:
            pkg.delete_config(project, azure_config)
            flash("Integration deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('integrations'))

@app.route('/atlassian-wiki', methods=['GET', 'POST'])
def add_atlassian_wiki():
    try:
        # Declare the atlassian wiki form
        form = AtlassianWikiForm(request.form)
        # Get current project
        project = request.cookies.get('project')  
        # get atlassian wiki parameter if provided
        atlassian_wiki_config = request.args.get('atlassian_wiki_config')
        if atlassian_wiki_config != None:
            output = pkg.get_atlassian_wiki_config_values(project, atlassian_wiki_config)
            form   = AtlassianWikiForm(output)               
        if form.validate_on_submit():
            # assign form data to variables
            pkg.save_atlassian_wiki( project, request.form.to_dict())
            atlassian_wiki_config = request.form.to_dict()["name"]
            flash("Integration added.")
        return render_template('integrations/atlassian-wiki.html', form = form, atlassian_wiki_config = atlassian_wiki_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))


@app.route('/delete/atlassian-wiki', methods=['GET'])
def delete_atlassian_wiki():
    try:
        # get atlassian wiki parameter if provided
        atlassian_wiki_config = None
        atlassian_wiki_config = request.args.get('atlassian_wiki_config')
        # Get current project
        project = request.cookies.get('project')  
        if atlassian_wiki_config != None:
            pkg.delete_config(project, atlassian_wiki_config)
            flash("Integration deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('integrations'))

@app.route('/atlassian-jira', methods=['GET', 'POST'])
def add_atlassian_jira():
    try:
        # Declare the atlassian jira form
        # Sema: should be created in forms.py
        form = AtlassianJiraForm(request.form)
        # Get current project
        project = request.cookies.get('project')  
        # get atlassian jira  parameter if provided
        atlassian_jira_config = request.args.get('atlassian_jira_config')
        if atlassian_jira_config != None:
            output = pkg.get_atlassian_jira_config_values(project, atlassian_jira_config)
            form   = AtlassianJiraForm(output)        
        if form.validate_on_submit():
            # assign form data to variables
            pkg.save_atlassian_jira( project, request.form.to_dict())
            atlassian_jira_config = request.form.to_dict()["name"]
            flash("Integration added.")
        return render_template('integrations/atlassian-jira.html', form = form, atlassian_jira_config = atlassian_jira_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))


@app.route('/delete/atlassian-jira', methods=['GET'])
def delete_atlassian_jira():
    try:
        # get atlassian jira parameter if provided
        atlassian_jira_config = None
        atlassian_jira_config = request.args.get('atlassian_jira_config')
        # Get current project
        project = request.cookies.get('project')  
        if atlassian_jira_config != None:
            pkg.delete_config(project, atlassian_jira_config)
            flash("Integration deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('integrations'))