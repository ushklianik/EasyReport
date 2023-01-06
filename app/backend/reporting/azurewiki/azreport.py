from app.backend import pkg
from app.backend.grafana.grafana import grafana
from app.backend.influxdb.influxdb import influxdb
from app.backend.azure.azure import azure


class azreport:

    def __init__(self, project, reportName):
        self.project        = project
        self.reportName     = reportName
        self.influxdbName   = None
        self.grafanaName    = None
        self.azureName      = None
        self.setConfig()
        self.grfanaObj      = grafana(project=self.project, name=self.grafanaName)
        self.influxdbObj    = influxdb(project=self.project, name=self.influxdbName)
        self.azureObj       = azure(project=self.project, name=self.azureName)

    def setConfig(self):
        config = pkg.getReportConfigValues(self.project, self.reportName)
        self.influxdbName = config["influxdbName"]
        self.grafanaName  = config["grafanaName"]
        self.azureName    = config["azureName"]  
        self.metrics      = config["graphs"]
    
    def generateReport(self, current_runId, reportType, baseline_runId = None):
        self.current_humanStartTime = self.influxdbObj.getHumanStartTime(current_runId)
        self.current_humanEndTime   = self.influxdbObj.getHumanEndTime(current_runId)

        self.current_startTime = self.influxdbObj.getStartTime(current_runId)
        self.current_endTime   = self.influxdbObj.getEndTime(current_runId)

        if baseline_runId != None:
            self.baseline_humanStartTime = self.influxdbObj.getHumanStartTime(baseline_runId)
            self.baseline_humanEndTime   = self.influxdbObj.getHumanEndTime(baseline_runId)

            self.baseline_startTime = self.influxdbObj.getStartTime(baseline_runId)
            self.baseline_endTime   = self.influxdbObj.getEndTime(baseline_runId)

            self.baseline_maxUsers = self.influxdbObj.getMaxActiveUsers(baseline_runId, self.baseline_startTime, self.baseline_endTime)

        self.current_maxUsers = self.influxdbObj.getMaxActiveUsers(current_runId, self.current_startTime, self.current_endTime)

    def pmetrics(self):
        print(self.metrics)