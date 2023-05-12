

# Flask modules
from flask                   import render_template, request, url_for, redirect, flash
from flask_login             import current_user

# App modules
from app         import app
from app.forms   import influxdb_form, grafana_form, azure_form, atlassian_wiki_form, atlassian_jira_form
from app.backend import pkg
import traceback


@app.route('/integrations')
def integrations():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
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
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Declare the Influxdb form
        form = influxdb_form(request.form)
        # get influxdb parameter if provided
        influxdb_config = request.args.get('influxdb_config')
        # Get current project
        project = request.cookies.get('project')  
        if influxdb_config != None:
            output = pkg.get_influxdb_config_values(project, influxdb_config)
            form = influxdb_form(output)               
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
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
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
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Declare the grafana form
        form = grafana_form(request.form)
        # Get current project
        project = request.cookies.get('project')  
        # get grafana parameter if provided
        grafana_config = request.args.get('grafana_config')
        if grafana_config != None:
            output = pkg.get_grafana_config_values(project, grafana_config)
            form = grafana_form(output)             
        if form.validate_on_submit():
            pkg.save_grafana( project, request.form.to_dict())
            grafana_config = request.form.to_dict()["name"]
            flash("Integration added.")
        return render_template('integrations/grafana.html', form = form, grafana_config = grafana_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))


@app.route('/delete/grafana', methods=['GET'])
def delete_grafana_config():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
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
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Declare the azure form
        form = azure_form(request.form)
        # Get current project
        project = request.cookies.get('project')  
        # get azure parameter if provided
        azure_config = request.args.get('azure_config')
        if azure_config != None:
            output = pkg.get_azure_config_values(project, azure_config)
            form = azure_form(output)             
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
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Declare the atlassian wiki form
        form = atlassian_wiki_form(request.form)
        # Get current project
        project = request.cookies.get('project')  
        # get atlassian wiki parameter if provided
        atlassian_wiki_config = request.args.get('atlassian_wiki_config')
        if atlassian_wiki_config != None:
            output = pkg.get_atlassian_wiki_config_values(project, atlassian_wiki_config)
            form   = atlassian_wiki_form(output)               
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
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Declare the atlassian jira form
        # Sema: should be created in forms.py
        form = atlassian_jira_form(request.form)
        # Get current project
        project = request.cookies.get('project')  
        # get atlassian jira  parameter if provided
        atlassian_jira_config = request.args.get('atlassian_jira_config')
        if atlassian_jira_config != None:
            output = pkg.get_atlassian_jira_config_values(project, atlassian_jira_config)
            form   = atlassian_jira_form(output)        
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