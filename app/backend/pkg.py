import os
from os import path as pt
from werkzeug.datastructures import MultiDict
import yaml
from datetime import datetime
import json
from app.models import Credentials


####################### OTHER:

def getFilesInDir(path):
    listOfValues = os.listdir(path)
    output = []
    for elem in listOfValues:
        if ".md" not in elem:
            output.append(elem)
    return output

def saveNewConfig(project, fl):
    pathToConfig = "./app/projects/" + project + "/config.json"
    with open(pathToConfig, 'w') as json_file:
        json.dump(fl, json_file, indent=4, separators=(',',': '))

def getJsonConfig(project):
    pathToConfig = "./app/projects/" + project + "/config.json"
    if pt.isfile(pathToConfig) is False or pt.getsize(pathToConfig) == 0:
        saveNewConfig(project, {})
    return open(pathToConfig, 'r')  

def validateConfig(project, key1, key2 = None):
    fl = json.load(getJsonConfig(project))
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
    saveNewConfig(project, fl)

def getProjects():
    return getFilesInDir("./app/projects/") 

def deleteConfig(project, config):
    validateConfig(project, "integrations", "influxdb")
    validateConfig(project, "integrations", "grafana")
    validateConfig(project, "integrations", "azure")
    validateConfig(project, "integrations", "conflwiki")
    validateConfig(project, "integrations", "confljira")
    validateConfig(project, "flowConfigs")

    fl = json.load(getJsonConfig(project))

    for idx, obj in enumerate(fl["integrations"]["influxdb"]):
        if obj["name"] == config:
            fl["integrations"]["influxdb"].pop(idx)

    for idx, obj in enumerate(fl["integrations"]["grafana"]):
        if obj["name"] == config:
            fl["integrations"]["grafana"].pop(idx)

    for idx, obj in enumerate(fl["integrations"]["azure"]):
        if obj["name"] == config:
            fl["integrations"]["azure"].pop(idx)  

    for idx, obj in enumerate(fl["integrations"]["conflwiki"]):
        if obj["name"] == config:
            fl["integrations"]["conflwiki"].pop(idx)

    for idx, obj in enumerate(fl["integrations"]["confljira"]):
        if obj["name"] == config:
            fl["integrations"]["confljira"].pop(idx)  

    for idx, obj in enumerate(fl["flowConfigs"]):
        if obj["name"] == config:
            fl["flowConfigs"].pop(idx)    

    saveNewConfig(project, fl)

####################### INFLUXDB:

def getInfluxdbConfigs(project):
    result = []
    validateConfig(project, "integrations", "influxdb")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["influxdb"]:
        result.append(config["name"])
    return result

def getInfluxdbConfigValues(project, influxdbConfig):
    validateConfig(project, "integrations", "influxdb")
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["integrations"]["influxdb"]:
        if item["name"] == influxdbConfig:
            for key in item:
                if "token_in_sql:" in item[key]:
                    value = Credentials.get(key=item[key])
                    output.add(key, value)
                else:
                    output.add(key, item[key])
    return output

def saveInfluxDB(project, form):
    validateConfig(project, "integrations", "influxdb")
    config_list = getInfluxdbConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    for key in form:
        if key != "csrf_token":
            if "Token" in key:
                cred = Credentials(key=key, value=form[key])
                value = cred.save()
                newConfig[key] = value
            else:
                newConfig[key] = form[key]

    if form["name"] not in config_list:
        fl["integrations"]["influxdb"].append(newConfig)
    else: 
        for idx, obj in enumerate(fl["integrations"]["influxdb"]):
            if obj["name"] == form["name"]:
                fl["integrations"]["influxdb"][idx] = newConfig

    saveNewConfig(project, fl)
    return "Influxdb added"

def getDefaultInfluxdb(project):
    validateConfig(project, "integrations", "influxdb")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["influxdb"]:
        if config["isDefault"] == "y":
            return config["name"]


####################### GRAFANA:

def getGrafanaConfigs(project):
    result = []
    validateConfig(project, "integrations", "grafana")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["grafana"]:
        result.append(config["name"])
    return result

def getGrafnaConfigValues(project, grafanaConfig):
    validateConfig(project, "integrations", "grafana")
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["integrations"]["grafana"]:
        if item["name"] == grafanaConfig:
            for key in item:
                if "token_in_sql:" in item[key]:
                    value = Credentials.get(key=item[key])
                    output.add(key, value)
                else:
                    output.add(key, item[key])
    return output

def saveGrafana(project, form):
    validateConfig(project, "integrations", "grafana")
    config_list = getGrafanaConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    for key in form:
        if key != "csrf_token":
            if "Token" in key:
                cred = Credentials(key=key, value=form[key])
                value = cred.save()
                newConfig[key] = value
            else:
                newConfig[key] = form[key]

    if form["name"] not in config_list:
        fl["integrations"]["grafana"].append(newConfig)
    else: 
        for idx, obj in enumerate(fl["integrations"]["grafana"]):
            if obj["name"] == form["name"]:
                fl["integrations"]["grafana"][idx] = newConfig
    
    saveNewConfig(project, fl)
    return "Grafana added"

def getDefaultGrafana(project):
    validateConfig(project, "integrations", "grafana")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["grafana"]:
        if config["isDefault"] == "y":
            return config["name"]

####################### OUTPUT:

def getOutputConfigs(project):
    result = []
    validateConfig(project, "integrations", "azure")
    validateConfig(project, "integrations", "conflwiki")
    validateConfig(project, "integrations", "confljira")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]:
        if config in ["azure","conflwiki","confljira"]:
            for integration in fl["integrations"][config]:
                result.append(integration["name"])
    return result

####################### AZURE:

def getAzureConfigs(project):
    result = []
    validateConfig(project, "integrations", "azure")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["azure"]:
        result.append(config["name"])
    return result

def getAzureConfigValues(project, azureConfig):
    validateConfig(project, "integrations", "azure")
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["integrations"]["azure"]:
        if item["name"] == azureConfig:
            for key in item:
                if "token_in_sql:" in item[key]:
                    value = Credentials.get(key=item[key])
                    output.add(key, value)
                else:
                    output.add(key, item[key])
    return output

def saveAzure(project, form):
    validateConfig(project, "integrations", "azure")
    config_list = getAzureConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    for key in form:
        if key != "csrf_token":
            if "Token" in key:
                cred = Credentials(key=key, value=form[key])
                value = cred.save()
                newConfig[key] = value
            else:
                newConfig[key] = form[key]

    if form["name"] not in config_list:
        fl["integrations"]["azure"].append(newConfig)
    else: 
        for idx, obj in enumerate(fl["integrations"]["azure"]):
            if obj["name"] == form["name"]:
                fl["integrations"]["azure"][idx] = newConfig
    
    saveNewConfig(project, fl)
    return "Azure added"

def getDefaultAzure(project):
    validateConfig(project, "integrations", "azure")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["azure"]:
        if config["isDefault"] == "y":
            return config["name"]

####################### FLOW CONFIG:          
        
def getFlowConfigs(project):
    validateConfig(project, "flowConfigs")
    result = []
    fl = json.load(getJsonConfig(project))
    if "flowConfigs" in fl:
        for config in fl["flowConfigs"]:
            result.append(config["name"])
        return result
    else: return []

def saveFlowConfig(project, form):
    validateConfig(project, "flowConfigs")
    config_list = getFlowConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    newConfig["graphs"] = []
    for key in form:
        if "graphs" in key:
            newConfig["graphs"].append({ "position": int(key[7:]), "name" : form[key] })
        elif key != "csrf_token":
            newConfig[key] = form[key]

    if form["name"] not in config_list:
        fl["flowConfigs"].append(newConfig)
    else: 
        for idx, obj in enumerate(fl["flowConfigs"]):
            if obj["name"] == form["name"]:
                fl["flowConfigs"][idx] = newConfig
    
    saveNewConfig(project, fl)
    return "Config added"

def getFlowConfigValuesInDict(project, flowConfig):
    validateConfig(project, "flowConfigs")
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["flowConfigs"]:
        if item["name"] == flowConfig:
            for key in item:
                if key == "graphs":
                    for graph in item[key]:
                        output.add(key+"-"+str(graph["position"]), graph["name"])
                else:
                    output.add(key, item[key])
    return output

def getFlowConfigValues(project, flowConfig):
    validateConfig(project, "flowConfigs")
    fl = json.load(getJsonConfig(project))
    output = {}
    for item in fl["flowConfigs"]:
        if item["name"] == flowConfig:
            for key in item:
                if key == "graphs":
                    output[key] = []
                    for x in range(len(item[key])):
                        output[key].append(item[key][x])
                else:
                    output[key] = item[key]
    return output
    
####################### GRAPHS:  

def getGraphs(project):
    validateConfig(project, "graphs")
    result = []
    fl = json.load(getJsonConfig(project))
    if "graphs" in fl:
        for config in fl["graphs"]:
            result.append(config["name"])
        return result
    else: return []

def getGraph(project, name):
    validateConfig(project, "graphs")
    fl = getJsonConfig(project)
    fl = json.load(getJsonConfig(project))
    for graph in fl["graphs"]:
        if graph["name"] == name:
            return graph
    return "no graph"

def saveGraph(project, form):
    validateConfig(project, "graphs")
    graphList = getGraphs(project)
    if form["name"] in graphList:
        return "Such name alrwady exixts"
    else:
        fl = json.load(getJsonConfig(project))
        newGraph = {}
        for key in form:
            if key != "csrf_token":
                newGraph[key] = form[key]

        fl["graphs"].append(newGraph)
        
        saveNewConfig(project, fl)
        return "Graph added"

def sortTests(tests):
    def startTime(e): return e['startTime']
    if len(tests) != 0:
        for test in tests:
            test["startTime"] = datetime.strftime(test["startTime"], "%Y-%m-%d %I:%M:%S %p")
            test["endTime"] = datetime.strftime(test["endTime"], "%Y-%m-%d %I:%M:%S %p")
    tests.sort(key=startTime, reverse=True)
    return tests

####################### CONFLUENCE WIKI:

def getDefaultConfl(project):
    validateConfig(project, "integrations", "conflwiki")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["conflwiki"]:
        if config["isDefault"] == "y":
            return config["name"]

def getConflWikiConfigs(project):
    result = []
    validateConfig(project, "integrations", "conflwiki")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["conflwiki"]:
        result.append(config["name"])
    return result

def getConflWikiConfigValues(project, azureConfig):
    validateConfig(project, "integrations", "conflwiki")
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["integrations"]["conflwiki"]:
        if item["name"] == azureConfig:
            for key in item:
                if "token_in_sql:" in item[key]:
                    value = Credentials.get(key=item[key])
                    output.add(key, value)
                else:
                    output.add(key, item[key])
    return output

def saveConfluenceWiki(project, form):
    validateConfig(project, "integrations", "conflwiki")
    config_list = getConflWikiConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    for key in form:
        if key != "csrf_token":
            if "Token" in key:
                cred = Credentials(key=key, value=form[key])
                value = cred.save()
                newConfig[key] = value
            else:
                newConfig[key] = form[key]

    if form["name"] not in config_list:
        fl["integrations"]["conflwiki"].append(newConfig)
    else: 
        for idx, obj in enumerate(fl["integrations"]["conflwiki"]):
            if obj["name"] == form["name"]:
                fl["integrations"]["conflwiki"][idx] = newConfig
    
    saveNewConfig(project, fl)
    return "Conflwiki added"

####################### CONFLUENCE JIRA:

def getDefaultJira(project):
    validateConfig(project, "integrations", "confljira")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["confljira"]:
        if config["isDefault"] == "y":
            return config["name"]

def getConflJiraConfigs(project):
    result = []
    validateConfig(project, "integrations", "confljira")
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["confljira"]:
        result.append(config["name"])
    return result

def getConflJiraConfigValues(project, azureConfig):
    validateConfig(project, "integrations", "confljira")
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["integrations"]["confljira"]:
        if item["name"] == azureConfig:
            for key in item:
                if "token_in_sql:" in item[key]:
                    value = Credentials.get(key=item[key])
                    output.add(key, value)
                else:
                    output.add(key, item[key])
    return output

def saveConfluenceJira(project, form):
    validateConfig(project, "integrations", "confljira")
    config_list = getConflJiraConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    for key in form:
        if key != "csrf_token":
            if "Token" in key:
                cred = Credentials(key=key, value=form[key])
                value = cred.save()
                newConfig[key] = value
            else:
                newConfig[key] = form[key]

    if form["name"] not in config_list:
        fl["integrations"]["confljira"].append(newConfig)
    else: 
        for idx, obj in enumerate(fl["integrations"]["confljira"]):
            if obj["name"] == form["name"]:
                fl["integrations"]["confljira"][idx] = newConfig
    
    saveNewConfig(project, fl)
    return "Confljira added"