import os
from os import path as pt
from werkzeug.datastructures import MultiDict
import yaml
from datetime import datetime
import json


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
            return {"status":"error", "message":"No config.json"}
    else:   
        return open(pathToConfig, 'r')  

def getProjects():
    return getFilesInDir("./app/projects/") 

def deleteConfig(project, config):
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

    for idx, obj in enumerate(fl["reportConfigs"]):
        if obj["name"] == config:
            fl["reportConfigs"].pop(idx)    

    saveNewConfig(project, fl)

####################### INFLUXDB:

def getInfluxdbConfigs(project):
    result = []
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["influxdb"]:
        result.append(config["name"])
    return result

def getInfluxdbConfigValues(project, influxdbConfig):
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["integrations"]["influxdb"]:
        if item["name"] == influxdbConfig:
            for key in item:
                output.add(key, item[key])
    return output

def saveInfluxDB(project, form):
    config_list = getInfluxdbConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    for key in form:
        if key != "csrf_token":
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
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["influxdb"]:
        if config["isDefault"] == "y":
            return config["name"]


####################### GRAFANA:

def getGrafanaConfigs(project):
    result = []
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["grafana"]:
        result.append(config["name"])
    return result

def getGrafnaConfigValues(project, grafanaConfig):
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["integrations"]["grafana"]:
        if item["name"] == grafanaConfig:
            for key in item:
                output.add(key, item[key])
    return output

def saveGrafana(project, form):
    config_list = getGrafanaConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    for key in form:
        if key != "csrf_token":
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
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["grafana"]:
        if config["isDefault"] == "y":
            return config["name"]

####################### AZURE:

def getAzureConfigs(project):
    result = []
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["azure"]:
        result.append(config["name"])
    return result

def getAzureConfigValues(project, azureConfig):
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["integrations"]["azure"]:
        if item["name"] == azureConfig:
            for key in item:
                output.add(key, item[key])
    return output

def saveAzure(project, form):
    config_list = getAzureConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    for key in form:
        if key != "csrf_token":
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
    fl = json.load(getJsonConfig(project))
    for config in fl["integrations"]["azure"]:
        if config["isDefault"] == "y":
            return config["name"]

####################### REPORT CONFIG:          
        
def getReportConfigs(project):
    result = []
    fl = json.load(getJsonConfig(project))
    for config in fl["reportConfigs"]:
        result.append(config["name"])
    return result

def saveReportConfig(project, form):
    config_list = getReportConfigs(project)
    fl = json.load(getJsonConfig(project))
    newConfig = {}
    newConfig["graphs"] = []
    for key in form:
        if "graphs" in key:
            newConfig["graphs"].append({ "position": int(key[8:]), "name" : form[key] })
        elif key != "csrf_token":
            newConfig[key] = form[key]

    if form["name"] not in config_list:
        fl["reportConfigs"].append(newConfig)
    else: 
        for idx, obj in enumerate(fl["reportConfigs"]):
            if obj["name"] == form["name"]:
                fl["reportConfigs"][idx] = newConfig
    
    saveNewConfig(project, fl)
    return "Config added"

def getReportConfigValuesInDict(project, reportConfig):
    fl = json.load(getJsonConfig(project))
    output = MultiDict()
    for item in fl["reportConfigs"]:
        if item["name"] == reportConfig:
            for key in item:
                if key == "graphs":
                    for graph in item[key]:
                        output.add(key+"-"+str(graph["position"]), graph["name"])
                else:
                    output.add(key, item[key])
    return output

def getReportConfigValues(project, reportConfig):
    fl = json.load(getJsonConfig(project))
    output = {}
    for item in fl["reportConfigs"]:
        if item["name"] == reportConfig:
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
    result = []
    fl = json.load(getJsonConfig(project))
    for config in fl["graphs"]:
        result.append(config["name"])
    return result

def saveGraph(project, form):
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
