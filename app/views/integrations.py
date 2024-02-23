# Copyright 2023 Uladzislau Shklianik <ushklianik@gmail.com> & Siamion Viatoshkin <sema.cod@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import traceback

from app         import app
from app.backend import pkg
from app.forms   import InfluxDBForm, GrafanaForm, AzureForm, AtlassianConfluenceForm, AtlassianJiraForm, SMTPMailForm
from flask       import render_template, request, url_for, redirect, flash


# Route for showing all integrations
@app.route('/integrations')
def integrations():
    try:
        # Get current project
        project = request.cookies.get('project')
        # Get integrations configs
        influxdb_configs             = pkg.get_integration_config_names(project, "influxdb")
        grafana_configs              = pkg.get_integration_config_names(project, "grafana")
        azure_configs                = pkg.get_integration_config_names(project, "azure")
        atlassian_confluence_configs = pkg.get_integration_config_names(project, "atlassian_confluence")
        atlassian_jira_configs       = pkg.get_integration_config_names(project, "atlassian_jira")
        smtp_mail_configs            = pkg.get_integration_config_names(project, "smtp_mail")
        return render_template('home/integrations.html',
                               influxdb_configs=influxdb_configs,
                               grafana_configs=grafana_configs,
                               azure_configs=azure_configs,
                               atlassian_confluence_configs=atlassian_confluence_configs,
                               atlassian_jira_configs=atlassian_jira_configs,
                               smtp_mail_configs=smtp_mail_configs
                               )
    except Exception as er:
        flash("ERROR: " + str(er))
        return render_template('home/integrations.html')

# Route for adding or updating InfluxDB integration
@app.route('/influxdb', methods=['GET', 'POST'])
def add_influxdb():
    # try:
        # Declare the Influxdb form
        form            = InfluxDBForm(request.form)
        # Get InfluxDB config parameter if provided
        influxdb_config = request.args.get('influxdb_config')
        # Get current project
        project = request.cookies.get('project')
        if influxdb_config is not None:
            output = pkg.get_influxdb_config_values(project, influxdb_config)
            form   = InfluxDBForm(output)
        if form.validate_on_submit():
            pkg.save_influxdb(project, request.form.to_dict())
            influxdb_config = request.form.to_dict()["name"]
            flash("Integration added.")
        return render_template('integrations/influxdb.html', form=form, influxdb_config=influxdb_config)
    # except Exception as er:
    #     flash("ERROR: " + str(er))
    #     return redirect(url_for('integrations'))

# Route for deleting InfluxDB integration
@app.route('/delete/influxdb', methods=['GET'])
def delete_influxdb():
    try:
        # Get InfluxDB config parameter if provided
        influxdb_config = request.args.get('influxdb_config')
        # Get current project
        project = request.cookies.get('project')
        if influxdb_config is not None:
            pkg.delete_config(project, influxdb_config)
            flash("Integration deleted.")
    except Exception:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for('integrations'))

# Route for adding or updating Grafana integration
@app.route('/grafana', methods=['GET', 'POST'])
def add_grafana():
    try:
        # Get current project
        project        = request.cookies.get('project')
        # Get Grafana config parameter if provided
        grafana_config = request.args.get('grafana_config')
        if request.method == 'POST':
            pkg.save_grafana(project, request.get_json())
            grafana_config = request.get_json()["name"]
            flash("Integration added.")
            return "grafana_config=" + grafana_config
        return render_template('integrations/grafana.html', grafana_config=grafana_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))

# Route for getting Grafana config
@app.route('/grafana-config', methods=['GET'])
def get_grafana_config():
    try:
        output         = "no data"
        # Get current project
        project        = request.cookies.get('project')
        # Get Grafana config parameter if provided
        grafana_config = request.args.get('grafana_config')
        if grafana_config is not None:
            output = pkg.get_grafana_config_values(project, grafana_config)
        return output
    except Exception as er:
        flash("ERROR: " + str(er))

# Route for deleting Grafana integration
@app.route('/delete/grafana', methods=['GET'])
def delete_grafana_config():
    try:
        # Get Grafana config parameter if provided
        grafana_config = request.args.get('grafana_config')
        # Get current project
        project        = request.cookies.get('project')
        if grafana_config is not None:
            pkg.delete_config(project, grafana_config)
            flash("Integration deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('integrations'))

# Route for adding or updating Azure integration
@app.route('/azure', methods=['GET', 'POST'])
def add_azure():
    try:
        # Declare the Azure form
        form         = AzureForm(request.form)
        # Get current project
        project      = request.cookies.get('project')
        # Get Azure config parameter if provided
        azure_config = request.args.get('azure_config')
        if azure_config is not None:
            output = pkg.get_azure_config_values(project, azure_config)
            form   = AzureForm(output)
        if form.validate_on_submit():
            # Assign form data to variables
            pkg.save_azure(project, request.form.to_dict())
            azure_config = request.form.to_dict()["name"]
            flash("Integration added.")
        return render_template('integrations/azure.html', form=form, azure_config=azure_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))

# Route for deleting Azure integration
@app.route('/delete/azure', methods=['GET'])
def delete_azure_config():
    try:
        # Get Azure config parameter if provided
        azure_config = request.args.get('azure_config')
        # Get current project
        project      = request.cookies.get('project')
        if azure_config is not None:
            pkg.delete_config(project, azure_config)
            flash("Integration deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('integrations'))

# Route for adding or updating Atlassian Confluence integration
@app.route('/atlassian-confluence', methods=['GET', 'POST'])
def add_atlassian_confluence():
    try:
        # Declare the Atlassian Confluence form
        form                  = AtlassianConfluenceForm(request.form)
        # Get current project
        project               = request.cookies.get('project')
        # Get Atlassian Confluence config parameter if provided
        atlassian_confluence_config = request.args.get('atlassian_confluence_config')
        if atlassian_confluence_config is not None:
            output = pkg.get_atlassian_confluence_config_values(project, atlassian_confluence_config)
            form   = AtlassianConfluenceForm(output)
        if form.validate_on_submit():
            # Assign form data to variables
            pkg.save_atlassian_confluence(project, request.form.to_dict())
            atlassian_confluence_config = request.form.to_dict()["name"]
            flash("Integration added.")
        return render_template('integrations/atlassian-confluence.html', form=form, atlassian_confluence_config=atlassian_confluence_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))

# Route for deleting Atlassian Confluence integration
@app.route('/delete/atlassian-confluence', methods=['GET'])
def delete_atlassian_confluence():
    try:
        # Get Atlassian Confluence config parameter if provided
        atlassian_confluence_config = request.args.get('atlassian_confluence_config')
        # Get current project
        project               = request.cookies.get('project')
        if atlassian_confluence_config is not None:
            pkg.delete_config(project, atlassian_confluence_config)
            flash("Integration deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('integrations'))

# Route for adding or updating Atlassian Jira integration
@app.route('/atlassian-jira', methods=['GET', 'POST'])
def add_atlassian_jira():
    try:
        # Declare the Atlassian Jira form
        form                  = AtlassianJiraForm(request.form)
        # Get current project
        project               = request.cookies.get('project')
        # Get Atlassian Jira config parameter if provided
        atlassian_jira_config = request.args.get('atlassian_jira_config')
        if atlassian_jira_config is not None:
            output = pkg.get_atlassian_jira_config_values(project, atlassian_jira_config)
            form   = AtlassianJiraForm(output)
        if form.validate_on_submit():
            # Assign form data to variables
            pkg.save_atlassian_jira(project, request.form.to_dict())
            atlassian_jira_config = request.form.to_dict()["name"]
            flash("Integration added.")
        return render_template('integrations/atlassian-jira.html', form=form, atlassian_jira_config=atlassian_jira_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))

# Route for deleting Atlassian Jira integration
@app.route('/delete/atlassian-jira', methods=['GET'])
def delete_atlassian_jira():
    try:
        # Get Atlassian Jira config parameter if provided
        atlassian_jira_config = request.args.get('atlassian_jira_config')
        # Get current project
        project               = request.cookies.get('project')
        if atlassian_jira_config is not None:
            pkg.delete_config(project, atlassian_jira_config)
            flash("Integration deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('integrations'))

# Route for adding or updating SMTP Mail integration
@app.route('/smtp-mail', methods=['GET', 'POST'])
def add_smtp_mail():
    try:
        # Get current project
        project          = request.cookies.get('project')
        # Get SMTP Mail config parameter if provided
        smtp_mail_config = request.args.get('smtp_mail_config')
        if request.method == 'POST':
            pkg.save_smtp_mail(project, request.get_json())
            smtp_mail_config = request.get_json()["name"]
            flash("Integration added.")
            return "smtp_mail_config=" + smtp_mail_config
        return render_template('integrations/smtp-mail.html', smtp_mail_config=smtp_mail_config)
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('integrations'))

# Route for getting SMTP Mail config
@app.route('/smtp-mail-config', methods=['GET'])
def get_smtp_mail_config():
    try:
        output           = "no data"
        # Get current project
        project          = request.cookies.get('project')
        # Get SMTP Mail config parameter if provided
        smtp_mail_config = request.args.get('smtp_mail_config')
        if smtp_mail_config is not None:
            output = pkg.get_smtp_mail_config_values(project, smtp_mail_config)
        return output
    except Exception as er:
        flash("ERROR: " + str(er))

# Route for deleting SMTP Mail integration
@app.route('/delete/smtp-mail', methods=['GET'])
def delete_smtp_mail_config():
    try:
        # Get SMTP Mail config parameter if provided
        smtp_mail_config = request.args.get('smtp_mail_config')
        # Get current project
        project          = request.cookies.get('project')
        if smtp_mail_config is not None:
            pkg.delete_config(project, smtp_mail_config)
            flash("Integration deleted.")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('integrations'))