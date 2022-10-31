from distutils.command.config import config
import os
from configparser import ConfigParser
from werkzeug.datastructures import MultiDict
import yaml

def getFilesInDir(path):
    listOfValues = os.listdir(path)
    output = []
    for elem in listOfValues:
        if ".md" not in elem:
            output.append(elem)
    return output

def getReports(project):
    return getFilesInDir("./app/projects/" + project + "/reports/")

def getInfluxdbConfigs(project):
    return getFilesInDir("./app/projects/" + project + "/integrations/influxdb/")

def getGrafanaConfigs(project):
    return getFilesInDir("./app/projects/" + project + "/integrations/grafana/")

def getAzureConfigs(project):
    return getFilesInDir("./app/projects/" + project + "/integrations/azure/")

def getReportConfigs(project):
    return getFilesInDir("./app/projects/" + project + "/reports/")

def getProjects():
    return getFilesInDir("./app/projects/")

def deleteConfig(path, config):
    configs = getFilesInDir(path)
    if config in configs:
        os.remove(path+config)

def deleteInfluxdbConfig(project, influxdbConfig):
    deleteConfig("./app/projects/" + project + "/integrations/influxdb/", influxdbConfig)

def deleteGrafana(project, grafanaConfig):
    deleteConfig("./app/projects/" + project + "/integrations/grafana/", grafanaConfig)

def deleteAzure(project, azureConfig):
    deleteConfig("./app/projects/" + project + "/integrations/azure/", azureConfig)

def deleteReport(project, reportConfig):
    deleteConfig("./app/projects/" + project + "/reports/", reportConfig)

def getInfluxdbConfigValues(project, influxdbConfig):
    config = {}
    with open("./app/projects/" + project + "/integrations/influxdb/"+influxdbConfig, "r") as f:
        config = yaml.safe_load(f)
    output = MultiDict()
    config = config["influxdb"]
    for item in config:
        output.add(item, config[item])
    return output

def saveInfluxDB(project, influxdbName, influxdbUrl, influxdbOrg, influxdbToken, influxdbTimeout, influxdbBucket, influxdbMeasurement, influxdbField):
    config_list = os.listdir("./app/projects/" + project + "/integrations/influxdb")
    for config in config_list:
        if influxdbName in config:
            return "Such name alrwady exixts"
    else:
        f = open("./app/projects/" + project + "/integrations/influxdb/"+influxdbName+".yaml", "a")
        f.write("influxdb:"                                     +"\n")
        f.write("  influxdbName: "        + influxdbName        +"\n")
        f.write("  influxdbUrl: "         + influxdbUrl         +"\n")
        f.write("  influxdbOrg: "         + influxdbOrg         +"\n")
        f.write("  influxdbToken: "       + influxdbToken       +"\n")
        f.write("  influxdbTimeout: "     + influxdbTimeout     +"\n")
        f.write("  influxdbBucket: "      + influxdbBucket      +"\n")
        f.write("  influxdbMeasurement: " + influxdbMeasurement +"\n")
        f.write("  influxdbField: "       + influxdbField       +"\n")
        f.write("  verify_ssl: False")
        return "Influxdb added"

def saveGrafana(project, grafanaName, grafanaServer, grafanaToken, grafanaDashboard, grafanaOrgId, grafanaDashRenderPath, grafanaDashRenderCompPath):
    config_list = os.listdir("./app/projects/" + project + "/integrations/grafana")
    for config in config_list:
        if grafanaName in config:
            return "Such name alrwady exixts"
    else:
        f = open("./app/projects/" + project + "/integrations/grafana/"+grafanaName+".yaml", "a")
        f.write("grafana:"                                             +"\n")
        f.write("  grafanaName: "               + grafanaName               +"\n")
        f.write("  grafanaServer: "             + grafanaServer             +"\n")
        f.write("  grafanaToken: "              + grafanaToken              +"\n")
        f.write("  grafanaDashboard: "          + grafanaDashboard          +"\n")
        f.write("  grafanaOrgId: "              + grafanaOrgId              +"\n")
        f.write("  grafanaDashRenderPath: "     + grafanaDashRenderPath     +"\n")
        f.write("  grafanaDashRenderCompPath: " + grafanaDashRenderCompPath +"\n")
        return "Grafana added"

def getGrafnaConfigValues(project, grafanaConfig):
    config = {}
    with open("./app/projects/" + project + "/integrations/grafana/"+grafanaConfig, "r") as f:
        config = yaml.safe_load(f)
    output = MultiDict()
    config = config["grafana"]
    for item in config:
        output.add(item, config[item])
    return output


def saveAzure(project, azureName, personalAccessToken, wikiOrganizationUrl, wikiProject, wikiIdentifier, wikiPathToReport, appInsighsLogsServer, appInsighsAppId, appInsighsApiKey):
    config_list = os.listdir("./app/projects/" + project + "/integrations/azure")
    for config in config_list:
        if azureName in config:
            return "Such name alrwady exixts"
    else:
        f = open("./app/projects/" + project + "/integrations/azure/"+azureName+".yaml", "a")
        f.write("azure:"                                             +"\n")
        f.write("  azureName: "               + azureName               +"\n")
        f.write("  personalAccessToken: "             + personalAccessToken             +"\n")
        f.write("  wikiOrganizationUrl: "              + wikiOrganizationUrl              +"\n")
        f.write("  wikiProject: "          + wikiProject          +"\n")
        f.write("  wikiIdentifier: "              + wikiIdentifier              +"\n")
        f.write("  wikiPathToReport: "     + wikiPathToReport     +"\n")
        f.write("  appInsighsLogsServer: " + appInsighsLogsServer +"\n")
        f.write("  appInsighsAppId: " + appInsighsAppId +"\n")
        f.write("  appInsighsApiKey: " + appInsighsApiKey +"\n")
        return "Azure added"

def getAzureConfigValues(project, azureConfig):
    config = {}
    with open("./app/projects/" + project + "/integrations/azure/"+azureConfig, "r") as f:
        config = yaml.safe_load(f)
    output = MultiDict()
    config = config["azure"]
    for item in config:
        output.add(item, config[item])
    return output

def getMetrics(project):
    return getFilesInDir("./app/projects/" + project + "/metrics/")

def saveReport(project, configs):
    if all(elem in configs for elem in ["influxdbName","grafanaName","azureName","reportName"]) and \
       any("metrics" in elem for elem in configs):
        reportName   =   configs["reportName"]
        influxdbName =   configs["influxdbName"]
        grafanaName  =   configs["grafanaName"]
        azureName    =   configs["azureName"]
        metrics      =   []
        for elem in configs: 
            if "metrics" in elem:
                metrics.append(configs[elem])
        if (len(metrics)>0):
            config_list = os.listdir("./app/projects/" + project + "/reports/")
            for config in config_list:
                 if reportName in config:
                    return "Such report name already exixts"
            else:
                f = open("./app/projects/" + project + "/reports/"+reportName+".yaml", "a")
                f.write("  reportName: "     + reportName          +"\n")
                f.write("  influxdbName: "   + influxdbName        +"\n")
                f.write("  grafanaName: "    + grafanaName         +"\n")
                f.write("  azureName: "      + azureName           +"\n")
                f.write("  metrics: "        + str(metrics)        +"\n")
                return "Report added"
        else:
            return "No metrics provided"

def getReportConfigValues(project, reportConfig):
    config = {}
    with open("./app/projects/" + project + "/reports/"+reportConfig, "r") as f:
        config = yaml.safe_load(f)
    output = MultiDict()
    for item in config:
        if item == "metrics":
            for x in range(len(config[item])):
                output.add(item+"-"+str(x), config[item][x])
        else:
            output.add(item, config[item])
    return output

def saveMetric(project, viewPanel, dashId, fileName, width, height):
    metricList = getMetrics(project)
    for metric in metricList:
        if fileName in metric:
            return "Such name alrwady exixts"
    else:
        f = open("./app/projects/" + project + "/metrics/"+fileName+".yaml", "a")
        f.write("viewPanel:"                + viewPanel               +"\n")
        f.write("dashId: "                  + dashId                  +"\n")
        f.write("fileName: "                + fileName                +"\n")
        f.write("width: "                   + width                   +"\n")
        f.write("height: "                  + height                  +"\n")
        return "Metric added"