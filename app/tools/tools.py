import os
from configparser import ConfigParser
from werkzeug.datastructures import MultiDict
import yaml

def getReports():
    report_list = os.listdir("./app/reports/")
    reports = []
    for report in report_list:
        reports.append(report)
    return reports

def getInfluxdbConfigs():
    config_list = os.listdir("./app/integrations/influxdb/")
    influxdbConfigs = []
    for config in config_list:
        influxdbConfigs.append(config)
    return influxdbConfigs

def getGrafanaConfigs():
    config_list = os.listdir("./app/integrations/grafana/")
    grafanaConfigs = []
    for config in config_list:
        grafanaConfigs.append(config)
    return grafanaConfigs


def getAzureConfigs():
    config_list = os.listdir("./app/integrations/azure/")
    azureConfigs = []
    for config in config_list:
        azureConfigs.append(config)
    return azureConfigs

def saveInfluxDB(influxdbName, influxdbUrl, influxdbOrg, influxdbToken, influxdbTimeout, influxdbBucket, influxdbMeasurement, influxdbField):
    config_list = os.listdir("./app/integrations/influxdb")
    for config in config_list:
        if influxdbName in config:
            return "Such name alrwady exixts"
    else:
        f = open("./app/integrations/influxdb/"+influxdbName+".yaml", "a")
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
    
def getInfluxdbConfigValues(influxdbConfig):
    config = {}
    with open("./app/integrations/influxdb/"+influxdbConfig, "r") as f:
        config = yaml.safe_load(f)
    output = MultiDict()
    config = config["influxdb"]
    for item in config:
        output.add(item, config[item])
    return output

def deleteInfluxdbConfig(influxdbConfig):
    influxdbConfigs = getInfluxdbConfigs()
    if influxdbConfig in influxdbConfigs:
        os.remove("./app/integrations/influxdb/"+influxdbConfig)

def saveGrafana(grafanaName, grafanaServer, grafanaToken, grafanaDashboard, grafanaOrgId, grafanaDashRenderPath, grafanaDashRenderCompPath):
    config_list = os.listdir("./app/integrations/grafana")
    for config in config_list:
        if grafanaName in config:
            return "Such name alrwady exixts"
    else:
        f = open("./app/integrations/grafana/"+grafanaName+".yaml", "a")
        f.write("grafana:"                                             +"\n")
        f.write("  grafanaName: "               + grafanaName               +"\n")
        f.write("  grafanaServer: "             + grafanaServer             +"\n")
        f.write("  grafanaToken: "              + grafanaToken              +"\n")
        f.write("  grafanaDashboard: "          + grafanaDashboard          +"\n")
        f.write("  grafanaOrgId: "              + grafanaOrgId              +"\n")
        f.write("  grafanaDashRenderPath: "     + grafanaDashRenderPath     +"\n")
        f.write("  grafanaDashRenderCompPath: " + grafanaDashRenderCompPath +"\n")
        return "Grafana added"

def deleteGrafana(grafanaConfig):
    grafanaConfigs = getGrafanaConfigs()
    if grafanaConfig in grafanaConfigs:
        os.remove("./app/integrations/grafana/"+grafanaConfig)

def getGrafnaConfigValues(grafanaConfig):
    config = {}
    with open("./app/integrations/grafana/"+grafanaConfig, "r") as f:
        config = yaml.safe_load(f)
    output = MultiDict()
    config = config["grafana"]
    for item in config:
        output.add(item, config[item])
    return output


def saveAzure(azureName, personalAccessToken, wikiOrganizationUrl, wikiProject, wikiIdentifier, wikiPathToReport, appInsighsLogsServer, appInsighsAppId, appInsighsApiKey):
    config_list = os.listdir("./app/integrations/azure")
    for config in config_list:
        if azureName in config:
            return "Such name alrwady exixts"
    else:
        f = open("./app/integrations/azure/"+azureName+".yaml", "a")
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

def deleteAzure(azureConfig):
    azureConfigs = getAzureConfigs()
    if azureConfig in azureConfigs:
        os.remove("./app/integrations/azure/"+azureConfig)

def getAzureConfigValues(azureConfig):
    config = {}
    with open("./app/integrations/azure/"+azureConfig, "r") as f:
        config = yaml.safe_load(f)
    output = MultiDict()
    config = config["azure"]
    for item in config:
        output.add(item, config[item])
    return output

def getMetrics():
    metric_list = os.listdir("./app/metrics/")
    metrics = []
    for metric in metric_list:
        metrics.append(metric)
    return metrics