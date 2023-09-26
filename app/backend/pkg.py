import os
from os import path as pt
from werkzeug.datastructures import MultiDict
from datetime import datetime
import json
from app.models import Credentials
import app.backend.pydantic_models as md
from app import config_path

def get_files_in_dir(path):
    listOfValues = os.listdir(path)
    output = []
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
            data[key1] = {}
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

def delete_config(project, config):
    # Define the integration types as a list of dictionaries
    integration_types = [
        {"list_name": "integrations", "key": "influxdb"},
        {"list_name": "integrations", "key": "grafana"},
        {"list_name": "integrations", "key": "azure"},
        {"list_name": "integrations", "key": "atlassian_wiki"},
        {"list_name": "integrations", "key": "atlassian_jira"},
        {"list_name": "integrations", "key": "smtp_mail"},
        {"list_name": "flows"},
        {"list_name": "templates"},
        {"list_name": "template_groups"}
    ]
    # Validate the config type
    for type in integration_types:
       if(type.get("key")):
           validate_config(project, type.get("list_name"), type.get("key"))
       else:
           validate_config(project, type.get("list_name"))
    # Load the configuration file
    data = get_project_config(project)
    # Iterate over the integration types and remove the config if it exists
    for key_obj in integration_types:
        if key_obj["list_name"] == "flows" or key_obj["list_name"] == "templates" or key_obj["list_name"] == "template_groups":
            for idx, obj in enumerate(data[key_obj["list_name"]]):
                if obj["name"] == config:
                    data[key_obj["list_name"]].pop(idx)
                    break
        else:
            for idx, obj in enumerate(data[key_obj["list_name"]][key_obj["key"]]):
                if obj["name"] == config:
                    data[key_obj["list_name"]][key_obj["key"]].pop(idx)
                    break
    # Save the updated configuration file
    save_new_data(project, data)

def get_integration_config_names(project, integration_name):
    return get_config_names(project, "integrations", integration_name)

def get_config_names(project, key1, key2 = None):
    result = []
    validate_config(project, key1, key2)
    data = get_project_config(project)
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
    data = get_project_config(project)
    output = MultiDict()
    for item in data["integrations"][integration_name]:
        if item["name"] == config_name:
            for key, value in item.items():
                output.add(key, check_if_token(value))
    return output

def get_json_values(project, json_name, config_name):
    validate_config(project, json_name)
    data = get_project_config(project)
    output = MultiDict()
    for item in data[json_name]:
        if item["name"] == config_name:
            for key, value in item.items():
                output.add(key, check_if_token(value))
    return output

def save_token(data):
    if "token" in data:
        cred = Credentials(key="token", value=data["token"])
        value = cred.save()
        data["token"] = value
    return data

def del_csrf_token(data):
    if 'csrf_token' in data:
       del data['csrf_token']
    return data

def save_integration(project, newdata, integration_type):
    validate_config(project, "integrations", integration_type)
    data = get_project_config(project)
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
    output = md.influxdb_model.parse_obj(get_integration_values(project, "influxdb", influxdb_config))
    return MultiDict(output.dict())

def save_influxdb(project, data):
    data = md.influxdb_model.parse_obj(data)
    save_integration(project, data.dict(), "influxdb")

def get_default_influxdb(project):
    return get_default_integration(project, "influxdb")


####################### GRAFANA:

def get_grafana_config_values(project, grafana_config):
    output = md.grafana_model.parse_obj(get_integration_values(project, "grafana", grafana_config))
    return output.dict()

def save_grafana(project, data):
    data = md.grafana_model.parse_obj(data)
    save_integration(project, data.dict(), "grafana")

def get_default_grafana(project):
    return get_default_integration(project, "grafana")

def get_dashboards(project):
    validate_config(project, "integrations", "grafana")
    data = get_project_config(project)
    output = []
    for item in data["integrations"]["grafana"]:
        if (item["dashboards"]):
            for id in item["dashboards"]:
                output.append(id)
    return output

####################### AZURE:

def get_azure_config_values(project, azure_config):
    output = md.azure_model.parse_obj(get_integration_values(project, "azure", azure_config))
    return MultiDict(output.dict())

def save_azure(project, data):
    data = md.azure_model.parse_obj(data)
    save_integration(project, data.dict(), "azure")

def get_default_azure(project):
    return get_default_integration(project, "azure")

####################### ATLASSIAN WIKI:

def get_atlassian_wiki_config_values(project, atlassian_wiki_config):
    output = md.atlassian_wiki_model.parse_obj(get_integration_values(project, "atlassian_wiki", atlassian_wiki_config))
    return MultiDict(output.dict())

def save_atlassian_wiki(project, data):
    data = md.atlassian_wiki_model.parse_obj(data)
    save_integration(project, data.dict(), "atlassian_wiki")

def get_default_atlassian_wiki(project):
    return get_default_integration(project, "atlassian_wiki")

####################### ATLASSIAN JIRA:

def get_atlassian_jira_config_values(project, atlassian_jira_config):
    output = md.atlassian_jira_model.parse_obj(get_integration_values(project, "atlassian_jira", atlassian_jira_config))
    return MultiDict(output.dict())

def save_atlassian_jira(project, data):
    data = md.atlassian_jira_model.parse_obj(data)
    save_integration(project, data.dict(), "atlassian_jira")

def get_default_atlassian_jira(project):
    return get_default_integration(project, "atlassian_jira")

####################### SMTP MAIL:

def get_smtp_mail_config_values(project, smtp_mail_config):
    output = md.smtp_mail_model.parse_obj(get_integration_values(project, "smtp_mail", smtp_mail_config))
    return output.dict()

def save_smtp_mail(project, data):
    data = md.smtp_mail_model.parse_obj(data)
    save_integration(project, data.dict(), "smtp_mail")

def get_default_smtp_mail(project):
    return get_default_integration(project, "smtp_mail")

def get_recipients(project):
    validate_config(project, "integrations", "smtp_mail")
    data = get_project_config(project)
    output = []
    for item in data["integrations"]["smtp_mail"]:
        if (item["recipients"]):
            for id in item["recipients"]:
                output.append(id)
    return output

####################### OUTPUT:

def get_output_configs(project):
    result=[]
    types = ["azure", "atlassian_wiki", "atlassian_jira", "smtp_mail"]
    for type in types:
        result += get_config_names(project, "integrations", type)
    return result

####################### FLOW CONFIG:

def save_flow_config(project, flow):
    validate_config(project, "flows")
    data = get_project_config(project)
    data["flows"] = save_dict(flow, data["flows"], get_config_names(project, "flows"))
    save_new_data(project, data)

def get_flow_values(project, flow):
    output = md.flow_model.parse_obj(get_json_values(project, "flows", flow))
    return output.dict()

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
    data = get_project_config(project)
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
    output = md.template_model.parse_obj(get_json_values(project, "templates", template))
    return output.dict()

def save_template(project, template):
    template = md.template_model.parse_obj(template)
    validate_config(project, "templates")
    data = get_project_config(project)
    data["templates"] = save_dict(template.dict(), data["templates"], get_config_names(project, "templates"))
    save_new_data(project, data)

def get_template_group_values(project, template_group):
    output = md.template_group_model.parse_obj(get_json_values(project, "template_groups", template_group))
    return output.dict()

def save_template_group(project, template_group):
    template_group = md.template_group_model.parse_obj(template_group)
    validate_config(project, "template_groups")
    data = get_project_config(project)
    data["template_groups"] = save_dict(template_group.dict(), data["template_groups"], get_config_names(project, "template_groups"))
    save_new_data(project, data)

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
    data = get_project_config(project)
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
            test["endTimestamp"] = str(int(test["endTime"].timestamp() * 1000))
            test["startTime"] = datetime.strftime(test["startTime"], "%Y-%m-%d %I:%M:%S %p")
            test["endTime"] = datetime.strftime(test["endTime"], "%Y-%m-%d %I:%M:%S %p")
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