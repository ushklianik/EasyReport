import os
from os import path as pt
from werkzeug.datastructures import MultiDict
from datetime import datetime
import json
from app.models import Credentials
import app.backend.pydantic_models as md

def get_files_in_dir(path):
    listOfValues = os.listdir(path)
    output = []
    for elem in listOfValues:
        if ".md" not in elem:
            output.append(elem)
    return output

def save_new_config(project, fl):
    pathToConfig = "./app/projects/" + project + "/config.json"
    with open(pathToConfig, 'w') as json_file:
        json.dump(fl, json_file, indent=4, separators=(',',': '))

def get_json_config(project):
    pathToConfig = "./app/projects/" + project + "/config.json"
    if pt.isfile(pathToConfig) is False or pt.getsize(pathToConfig) == 0:
        save_new_config(project, {})
    return open(pathToConfig, 'r')  

def validate_config(project, key1, key2 = None):
    fl = json.load(get_json_config(project))
    if key2 == None:
        if key1 not in fl:
            fl[key1] = []
    else:
        if key1 not in fl:
            fl[key1] = {}
            fl[key1][key2] = []
        else:
            if key2 not in fl[key1]:
                fl[key1][key2] = []
    save_new_config(project, fl)

def get_projects():
    return get_files_in_dir("./app/projects/") 

def delete_config(project, config):
    # Define the integration types as a list of dictionaries
    integration_types = [
        {"list_name": "integrations", "key": "influxdb"},
        {"list_name": "integrations", "key": "grafana"},
        {"list_name": "integrations", "key": "azure"},
        {"list_name": "integrations", "key": "atlassian_wiki"},
        {"list_name": "integrations", "key": "atlassian_jira"},
        {"list_name": "flow_configs"}
    ]
    # Validate the config type
    for type in integration_types:
       if(type.get("key")):
           validate_config(project, type.get("list_name"), type.get("key"))
       else:
           validate_config(project, type.get("list_name"))
    # Load the configuration file
    fl = json.load(get_json_config(project))
    # Iterate over the integration types and remove the config if it exists
    for key_obj in integration_types:
        if key_obj["list_name"] == "flow_configs":
            for idx, obj in enumerate(fl[key_obj["list_name"]]):
                if obj["name"] == config:
                    fl[key_obj["list_name"]].pop(idx)
                    break
        else:
            for idx, obj in enumerate(fl[key_obj["list_name"]][key_obj["key"]]):
                if obj["name"] == config:
                    fl[key_obj["list_name"]][key_obj["key"]].pop(idx)
                    break
    # Save the updated configuration file
    save_new_config(project, fl)

def get_integration_config_names(project, integration_name):
    return get_config_names(project, "integrations", integration_name)

def get_config_names(project, key1, key2 = None):
    result = []
    validate_config(project, key1, key2)
    fl = json.load(get_json_config(project))
    if (key2):
        for key in fl[key1][key2]:
            result.append(key["name"])
    else:
        for key in fl[key1]:
            result.append(key["name"])
    return result

def check_if_token(value):
    if "token_in_sql:" in value:
        value = Credentials.get(value)
    return value

def get_integration_values(project, integration_name, config_name):
    validate_config(project, "integrations", integration_name)
    fl = json.load(get_json_config(project))
    output = MultiDict()
    for item in fl["integrations"][integration_name]:
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

def save_integration(project, data, integration_type):
    validate_config(project, "integrations", integration_type)
    fl = json.load(get_json_config(project))
    fl["integrations"][integration_type] = save_dict(data,  fl["integrations"][integration_type], get_integration_config_names(project, integration_type))
    save_new_config(project, fl)

def get_default_integration(project, integration_type):
    validate_config(project, "integrations", integration_type)
    fl = json.load(get_json_config(project))
    for config in fl["integrations"][integration_type]:
        if config["is_default"] == "true":
            return config["name"]
        
def save_dict(data, fl, list):
    data = del_csrf_token(data)
    data = save_token(data)
    if data["name"] not in list: fl.append(data)
    else: 
        for idx, obj in enumerate(fl):
            if obj["name"] == data["name"]:
                fl[idx] = data
    return fl

####################### INFLUXDB:

def get_influxdb_config_values(project, influxdb_config):
    output = md.influxdb_model.parse_obj(get_integration_values(project, "influxdb", influxdb_config))
    return MultiDict(output.dict())

def save_influxdb(project, data):
    data = md.influxdb_model.parse_obj(data)
    save_integration(project, data.dict(), "influxdb")

def get_default_influxdb(project):
    data = md.influxdb_model.parse_obj(get_default_integration(project, "influxdb"))
    return data.dict()


####################### GRAFANA:

def get_grafana_config_values(project, grafana_config):
    output = md.grafana_model.parse_obj(get_integration_values(project, "grafana", grafana_config))
    return output.dict()

def save_grafana(project, data):
    data = md.grafana_model.parse_obj(data)
    save_integration(project, data.dict(), "grafana")

def get_default_grafana(project):
    data = md.grafana_model.parse_obj(get_default_integration(project, "grafana"))
    return data.dict()

def get_dashboards(project):
    validate_config(project, "integrations", "grafana")
    fl = json.load(get_json_config(project))
    output = []
    for item in fl["integrations"]["grafana"]:
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
    data = md.azure_model.parse_obj(get_default_integration(project, "azure"))
    return data.dict()
        
####################### ATLASSIAN WIKI:

def get_atlassian_wiki_config_values(project, atlassian_wiki_config):
    output = md.atlassian_wiki_model.parse_obj(get_integration_values(project, "atlassian_wiki", atlassian_wiki_config))
    return MultiDict(output.dict())

def save_atlassian_wiki(project, data):
    data = md.atlassian_wiki_model.parse_obj(data)
    save_integration(project, data.dict(), "atlassian_wiki")

def get_default_atlassian_wiki(project):
    data = md.atlassian_wiki_model.parse_obj(get_default_integration(project, "atlassian_wiki"))
    return data.dict()

####################### ATLASSIAN JIRA:
        
def get_atlassian_jira_config_values(project, atlassian_jira_config):
    output = md.atlassian_jira_model.parse_obj(get_integration_values(project, "atlassian_jira", atlassian_jira_config))
    return MultiDict(output.dict())

def save_atlassian_jira(project, data):
    data = md.atlassian_jira_model.parse_obj(data)
    save_integration(project, data.dict(), "atlassian_jira")

def get_default_atlassian_jira(project):
    data = md.atlassian_jira_model.parse_obj(get_default_integration(project, "atlassian_jira"))
    return data.dict()
        
####################### OUTPUT:

def get_output_configs(project):
    result=[]
    types = ["azure", "atlassian_wiki", "atlassian_jira"]
    for type in types:
        result += get_config_names(project, "integrations", type)
    return result

####################### FLOW CONFIG:         

def get_flow_config_values_in_dict(project, flow_config):
    validate_config(project, "flow_configs")
    fl = json.load(get_json_config(project))
    output = MultiDict()
    for item in fl["flow_configs"]:
        if item["name"] == flow_config:
            for key in item:
                if key == "graphs":
                    for graph in item[key]:
                        output.add(key+"-"+str(graph["position"]), graph["name"])
                else:
                    output.add(key, item[key])
    return output   

def save_flow_config(project, form):
    validate_config(project, "flow_configs")
    fl = json.load(get_json_config(project))
    newConfig = {}
    newConfig["graphs"] = []
    for key in form:
        if "graphs" in key:
            newConfig["graphs"].append({ "position": int(key[7:]), "name" : form[key] })
        else:
            newConfig[key] = form[key]
    fl["flow_configs"] = save_dict(form, fl["flow_configs"], get_config_names(project, "flow_configs"))
    save_new_config(project, fl)
    
####################### GRAPHS:  

def get_graph(project, name):
    validate_config(project, "graphs")
    fl = json.load(get_json_config(project))
    for graph in fl["graphs"]:
        if graph["name"] == name:
            return graph

def get_graphs(project):
    validate_config(project, "graphs")
    fl = json.load(get_json_config(project))
    return fl["graphs"]

def save_graph(project, form):
    validate_config(project, "graphs")
    fl = json.load(get_json_config(project))
    fl["graphs"] = save_dict(form, fl["graphs"], get_config_names(project, "graphs"))
    save_new_config(project, fl)

####################### OTHER:  
def sort_tests(tests):
    def start_time(e): return e['startTime']
    if len(tests) != 0:
        for test in tests:
            test["startTime"] = datetime.strftime(test["startTime"], "%Y-%m-%d %I:%M:%S %p")
            test["endTime"] = datetime.strftime(test["endTime"], "%Y-%m-%d %I:%M:%S %p")
    tests.sort(key=start_time, reverse=True)
    return tests