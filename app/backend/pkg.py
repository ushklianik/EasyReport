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

import app.backend.pydantic_models as md
import os
import json

from app                     import config_path
from app.models              import Credentials
from os                      import path as pt
from werkzeug.datastructures import MultiDict
from datetime                import datetime


def get_files_in_dir(path):
    listOfValues = os.listdir(path)
    output       = []
    for elem in listOfValues:
        if ".md" not in elem:
            output.append(elem)
    return output

def save_new_config(data):
    path_to_config = config_path
    # Save the updated configuration
    with open(path_to_config, 'w') as json_file:
        json.dump(data, json_file, indent=4, separators=(',', ': '))

def save_new_data(project, data):
    path_to_config = config_path
    # Load existing configuration if it exists
    if os.path.exists(path_to_config):
        with open(path_to_config, 'r') as json_file:
            if os.path.getsize(path_to_config) != 0:
                config = json.load(json_file)
            else:
                config = []
    else:
        config = []
    # Update or add the project's data
    for obj in config:
        if obj["name"] == project:
            obj["data"] = data
            break
    else:
        config.append({"name": project, "data": data})
    # Save the updated configuration
    with open(path_to_config, 'w') as json_file:
        json.dump(config, json_file, indent=4, separators=(',', ': '))

def get_json_config():
    path_to_config = config_path
    if pt.isfile(path_to_config) is False or pt.getsize(path_to_config) == 0:
        return []
    with open(path_to_config, 'r') as json_file:
        config = json.load(json_file)
    return config

def get_project_config(project):
    config = get_json_config()
    for obj in config:
        if obj["name"] == project:
            return obj["data"]
    return {}

def validate_config(project, key1, key2 = None):
    data = get_project_config(project)
    if key2 == None:
        if key1 not in data:
            data[key1] = []
    else:
        if key1 not in data:
            data[key1]       = {}
            data[key1][key2] = []
        else:
            if key2 not in data[key1]:
                data[key1][key2] = []
    save_new_data(project, data)

def get_projects():
    config = get_json_config()
    result = []
    for obj in config:
        result.append(obj["name"])
    return result

def get_project_stats(project):
    result = {}
    result["integrations"] = 0
    result["flows"]        = 0
    result["graphs"]       = 0
    result["nfrs"]         = 0
    result["templates"]    = 0
    validate_config(project, "integrations", "influxdb")
    data = get_project_config(project)
    for integration in data["integrations"]:
        result["integrations"] += len(data["integrations"][integration])
    validate_config(project, "flows")
    data = get_project_config(project)
    result["flows"] = len(data["flows"])
    validate_config(project, "graphs")
    data = get_project_config(project)
    result["graphs"] = len(data["graphs"])
    validate_config(project, "templates")
    data = get_project_config(project)
    result["templates"] = len(data["templates"])
    validate_config(project, "nfrs")
    data = get_project_config(project)
    result["nfrs"] = len(data["nfrs"])
    return result

def delete_config(project, config, list_name, type):
    # Validate the config type
    if(type):
        validate_config(project, list_name, type)
    else:
        validate_config(project, list_name)
    # Load the configuration file
    data = get_project_config(project)
    # Remove the config if it exists
    if list_name == "flows" or list_name == "templates" or list_name == "template_groups":
        for idx, obj in enumerate(data[list_name]):
            if obj["name"] == config:
                data[list_name].pop(idx)
    else:
        for idx, obj in enumerate(data[list_name][type]):
            if obj["name"] == config:
                data[list_name][type].pop(idx)
    save_new_data(project, data)

def get_integration_config_names(project, integration_name):
    return get_config_names(project, "integrations", integration_name)

def get_config_names(project, key1, key2 = None):
    result = []
    validate_config(project, key1, key2)
    data   = get_project_config(project)
    if (key2):
        for key in data[key1][key2]:
            result.append(key["name"])
    else:
        for key in data[key1]:
            result.append(key["name"])
    return result

def check_if_token(value):
    if isinstance(value, str):
        if "token_in_sql:" in value:
            value = Credentials.get(value)
    return value

def get_integration_values(project, integration_name, config_name):
    validate_config(project, "integrations", integration_name)
    data   = get_project_config(project)
    output = MultiDict()
    for item in data["integrations"][integration_name]:
        if item["name"] == config_name:
            for key, value in item.items():
                output.add(key, check_if_token(value))
    return output

def get_json_values(project, json_name, config_name):
    validate_config(project, json_name)
    data   = get_project_config(project)
    output = MultiDict()
    for item in data[json_name]:
        if item["name"] == config_name:
            for key, value in item.items():
                output.add(key, check_if_token(value))
    return output

def save_token(data):
    if "token" in data:
        cred          = Credentials(key="token", value=data["token"])
        value         = cred.save()
        data["token"] = value
    return data

def del_csrf_token(data):
    if 'csrf_token' in data:
       del data['csrf_token']
    return data

def save_integration(project, newdata, integration_type):
    validate_config(project, "integrations", integration_type)
    data                                   = get_project_config(project)
    data["integrations"][integration_type] = save_dict(newdata, data["integrations"][integration_type], get_integration_config_names(project, integration_type))
    save_new_data(project, data)

def get_default_integration(project, integration_type):
    validate_config(project, "integrations", integration_type)
    data = get_project_config(project)
    for config in data["integrations"][integration_type]:
        if config["is_default"] == "true":
            return config["name"]
        
def save_dict(newdata, data, list):
    newdata = del_csrf_token(newdata)
    newdata = save_token(newdata)
    if newdata["name"] not in list: data.append(newdata)
    else: 
        for idx, obj in enumerate(data):
            if obj["name"] == newdata["name"]:
                data[idx] = newdata
    return data

####################### INFLUXDB:

def get_influxdb_config_values(project, influxdb_config):
    output = md.InfluxdbModel.parse_obj(get_integration_values(project, "influxdb", influxdb_config))
    return MultiDict(output.dict())

def save_influxdb(project, data):
    data = md.InfluxdbModel.parse_obj(data)
    save_integration(project, data.dict(), "influxdb")

def get_default_influxdb(project):
    return get_default_integration(project, "influxdb")

def delete_influxdb_config(project, config):
    delete_config(project, config, "integrations", "influxdb")

####################### GRAFANA:

def get_grafana_config_values(project, grafana_config):
    output = md.GrafanaModel.parse_obj(get_integration_values(project, "grafana", grafana_config))
    return output.dict()

def save_grafana(project, data):
    data = md.GrafanaModel.parse_obj(data)
    save_integration(project, data.dict(), "grafana")

def get_default_grafana(project):
    return get_default_integration(project, "grafana")

def get_dashboards(project):
    validate_config(project, "integrations", "grafana")
    data   = get_project_config(project)
    output = []
    for item in data["integrations"]["grafana"]:
        if (item["dashboards"]):
            for id in item["dashboards"]:
                output.append(id)
    return output

def delete_grafana_config(project, config):
    delete_config(project, config, "integrations", "grafana")

####################### AZURE:

def get_azure_config_values(project, azure_config):
    output = md.AzureModel.parse_obj(get_integration_values(project, "azure", azure_config))
    return MultiDict(output.dict())

def save_azure(project, data):
    data = md.AzureModel.parse_obj(data)
    save_integration(project, data.dict(), "azure")

def get_default_azure(project):
    return get_default_integration(project, "azure")

def delete_azure_config(project, config):
    delete_config(project, config, "integrations", "azure")

####################### ATLASSIAN WIKI:

def get_atlassian_wiki_config_values(project, atlassian_wiki_config):
    output = md.AtlassianWikiModel.parse_obj(get_integration_values(project, "atlassian_wiki", atlassian_wiki_config))
    return MultiDict(output.dict())

def save_atlassian_wiki(project, data):
    data = md.AtlassianWikiModel.parse_obj(data)
    save_integration(project, data.dict(), "atlassian_wiki")

def get_default_atlassian_wiki(project):
    return get_default_integration(project, "atlassian_wiki")

def delete_atlassian_wiki_config(project, config):
    delete_config(project, config, "integrations", "atlassian_wiki")

####################### ATLASSIAN JIRA:

def get_atlassian_jira_config_values(project, atlassian_jira_config):
    output = md.AtlassianJiraModel.parse_obj(get_integration_values(project, "atlassian_jira", atlassian_jira_config))
    return MultiDict(output.dict())

def save_atlassian_jira(project, data):
    data = md.AtlassianJiraModel.parse_obj(data)
    save_integration(project, data.dict(), "atlassian_jira")

def get_default_atlassian_jira(project):
    return get_default_integration(project, "atlassian_jira")

def delete_atlassian_jira_config(project, config):
    delete_config(project, config, "integrations", "atlassian_jira")

####################### SMTP MAIL:

def get_smtp_mail_config_values(project, smtp_mail_config):
    output = md.SmtpMailModel.parse_obj(get_integration_values(project, "smtp_mail", smtp_mail_config))
    return output.dict()

def save_smtp_mail(project, data):
    data = md.SmtpMailModel.parse_obj(data)
    save_integration(project, data.dict(), "smtp_mail")

def get_default_smtp_mail(project):
    return get_default_integration(project, "smtp_mail")

def get_recipients(project):
    validate_config(project, "integrations", "smtp_mail")
    data   = get_project_config(project)
    output = []
    for item in data["integrations"]["smtp_mail"]:
        if (item["recipients"]):
            for id in item["recipients"]:
                output.append(id)
    return output

def delete_smtp_mail_config(project, config):
    delete_config(project, config, "integrations", "smtp_mail")

####################### OUTPUT:

def get_output_configs(project):
    result = []
    types  = ["azure", "atlassian_wiki", "atlassian_jira", "smtp_mail"]
    for type in types:
        result += get_config_names(project, "integrations", type)
    return result

####################### FLOW CONFIG:

def save_flow_config(project, flow):
    validate_config(project, "flows")
    data          = get_project_config(project)
    data["flows"] = save_dict(flow, data["flows"], get_config_names(project, "flows"))
    save_new_data(project, data)

def get_flow_values(project, flow):
    output = md.FlowModel.parse_obj(get_json_values(project, "flows", flow))
    return output.dict()
       
def delete_flow_config(project, config):
    delete_config(project, config, "flows")

####################### NFRS CONFIG:

def get_nfr(project, name):
    validate_config(project, "nfrs")
    data = get_project_config(project)
    for nfr in data["nfrs"]:
        if nfr["name"] == name:
            return nfr

def get_nfrs(project):
    validate_config(project, "nfrs")
    data = get_project_config(project)
    return data["nfrs"]

def save_nfrs(project, nfrs):
    validate_config(project, "nfrs")
    data         = get_project_config(project)
    data["nfrs"] = save_dict(nfrs, data["nfrs"], get_config_names(project, "nfrs"))
    save_new_data(project, data)

def delete_nfr(project, name):
    validate_config(project, "nfrs")
    data = get_project_config(project)
    for idx, obj in enumerate(data["nfrs"]):
        if obj["name"] == name:
            data["nfrs"].pop(idx)
            break
    save_new_data(project, data)

####################### TEMPLATE CONFIG: 

def get_template_values(project, template):
    output = md.TemplateModel.parse_obj(get_json_values(project, "templates", template))
    return output.dict()

def save_template(project, template):
    template          = md.TemplateModel.parse_obj(template)
    validate_config(project, "templates")
    data              = get_project_config(project)
    data["templates"] = save_dict(template.dict(), data["templates"], get_config_names(project, "templates"))
    save_new_data(project, data)

def get_template_group_values(project, template_group):
    output = md.TemplateGroupModel.parse_obj(get_json_values(project, "template_groups", template_group))
    return output.dict()

def save_template_group(project, template_group):
    template_group          = md.TemplateGroupModel.parse_obj(template_group)
    validate_config(project, "template_groups")
    data                    = get_project_config(project)
    data["template_groups"] = save_dict(template_group.dict(), data["template_groups"], get_config_names(project, "template_groups"))
    save_new_data(project, data)

def delete_template_config(project, config):
    delete_config(project, config, "templates")
    
def delete_template_group_config(project, config):
    delete_config(project, config, "template_groups")

####################### GRAPHS:

def get_graph(project, name):
    validate_config(project, "graphs")
    data = get_project_config(project)
    for graph in data["graphs"]:
        if graph["name"] == name:
            return graph

def check_graph(project, name):
    validate_config(project, "graphs")
    data = get_project_config(project)
    for graph in data["graphs"]:
        if graph["name"] == name:
            return True
    return False

def get_graphs(project):
    validate_config(project, "graphs")
    data = get_project_config(project)
    return data["graphs"]

def save_graph(project, form):
    validate_config(project, "graphs")
    data           = get_project_config(project)
    data["graphs"] = save_dict(form, data["graphs"], get_config_names(project, "graphs"))
    save_new_data(project, data)

def delete_graph(project, graph_name):
    validate_config(project, "graphs")
    data = get_project_config(project)
    for idx, obj in enumerate(data["graphs"]):
        if obj["name"] == graph_name:
            data["graphs"].pop(idx)
            break
    save_new_data(project, data)

####################### OTHER:
def sort_tests(tests):
    def start_time(e): return e['startTime']
    if len(tests) != 0:
        for test in tests:
            test["startTimestamp"] = str(int(test["startTime"].timestamp() * 1000))
            test["endTimestamp"]   = str(int(test["endTime"].timestamp() * 1000))
            test["startTime"]      = datetime.strftime(test["startTime"], "%Y-%m-%d %I:%M:%S %p")
            test["endTime"]        = datetime.strftime(test["endTime"], "%Y-%m-%d %I:%M:%S %p")
    tests.sort(key=start_time, reverse=True)
    return tests

def save_project(project):
    save_new_data(project, {})

def delete_project(project):
    data = get_json_config()
    for idx, obj in enumerate(data):
        if obj["name"] == project:
            data.pop(idx)
            break
    save_new_config(data)