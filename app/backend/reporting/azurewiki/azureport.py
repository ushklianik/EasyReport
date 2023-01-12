from app.backend import pkg
from app.backend.grafana.grafana import grafana
from app.backend.influxdb.influxdb import influxdb
from app.backend.azure.azure import azure
from datetime import datetime
import threading

class azureport:

    def __init__(self, project, reportName):
        self.project        = project
        self.reportName     = reportName
        self.influxdbName   = None
        self.grafanaName    = None
        self.azureName      = None
        self.setConfig()
        self.grafanaObj     = grafana(project=self.project, name=self.grafanaName)
        self.influxdbObj    = influxdb(project=self.project, name=self.influxdbName)
        self.azureObj       = azure(project=self.project, name=self.azureName)
        self.progress       = 0
        self.status         = "Not started"

    def setConfig(self):
        config = pkg.getReportConfigValues(self.project, self.reportName)
        self.influxdbName = config["influxdbName"]
        self.grafanaName  = config["grafanaName"]
        self.azureName    = config["azureName"]  
        self.graphs       = config["graphs"]
    
    def generateReport(self, current_runId, baseline_runId = None):
        self.influxdbObj.connectToInfluxDB()
        self.current_humanStartTime = self.influxdbObj.getHumanStartTime(current_runId)
        self.current_humanEndTime   = self.influxdbObj.getHumanEndTime(current_runId)
        self.current_startTime = self.influxdbObj.getStartTime(current_runId)
        self.current_endTime   = self.influxdbObj.getEndTime(current_runId)
        self.current_startTmp  = self.influxdbObj.getStartTmp(current_runId)
        self.current_endTmp    = self.influxdbObj.getEndTmp(current_runId)
        self.testName = self.influxdbObj.getTestName(current_runId, self.current_startTime, self.current_endTime)
        current_grafanaLink    = self.grafanaObj.getGrafanaTestLink(self.current_startTmp, self.current_endTmp, self.testName, current_runId)
        if baseline_runId != None:
            self.baseline_humanStartTime = self.influxdbObj.getHumanStartTime(baseline_runId)
            self.baseline_humanEndTime   = self.influxdbObj.getHumanEndTime(baseline_runId)
            self.baseline_startTime = self.influxdbObj.getStartTime(baseline_runId)
            self.baseline_endTime   = self.influxdbObj.getEndTime(baseline_runId)
            self.baseline_startTmp  = self.influxdbObj.getStartTmp(baseline_runId)
            self.baseline_endTmp    = self.influxdbObj.getEndTmp(baseline_runId)
            self.baseline_maxUsers = self.influxdbObj.getMaxActiveUsers(baseline_runId, self.baseline_startTime, self.baseline_endTime)
            baseline_grafanaLink    = self.grafanaObj.getGrafanaTestLink(self.baseline_startTmp, self.baseline_endTmp, self.testName, baseline_runId)

        self.current_maxUsers = self.influxdbObj.getMaxActiveUsers(current_runId, self.current_startTime, self.current_endTime)

        self.status = "Collected data from InfluxDB"
        self.progress = 25

        screenshots = self.grafanaObj.renderImage(self.graphs, self.current_startTime, self.current_endTime, self.testName, current_runId)

        self.status = "Rendered images in Grafana"
        self.progress = 50

        for screenshot in screenshots:
            fileName = self.azureObj.putImageToAzure(screenshot["image"], screenshot["name"])
            screenshot["filename"] = fileName

        self.status = "Uploaded images to Azure"
        self.progress = 75

        wikiPageName = str(self.current_maxUsers) + " users | Azure candidate | " + self.current_humanStartTime
        wikiPagePath = self.azureObj.getPath() + "/" + self.testName + "/" + wikiPageName
        body = '''##Status: `To fill in manually`\n'''
        body +='''
[[_TOC_]]

# Summary
 - To fill in manually

# Test settings
|vUsers | Duration | Start time | End time | Comments | Grafana dashboard |
|--|--|--|--|--|--|--|--|
|'''+str(self.current_maxUsers)+''' |'''+str(int(self.current_endTmp-self.current_startTmp))+''' sec |'''+str(self.current_humanStartTime)+''' |'''+str(self.current_humanEndTime)+''' | Current test | [Grafana link]('''+current_grafanaLink+''') |
'''
        if baseline_runId != None:
            body +='''|'''+str(self.baseline_maxUsers)+''' |'''+str(int(self.current_endTmp-self.current_startTmp))+''' sec |'''+str(self.baseline_humanStartTime)+''' |'''+str(self.baseline_humanEndTime)+''' | Baseline test | [Grafana link]('''+baseline_grafanaLink+''') |
            '''
        for idx in range(len(screenshots)):
            for screenshot in screenshots:
                if idx == screenshot["position"]:
                    body = body + '''\n'''
                    body = body + '''## ''' + str(screenshot["name"])
                    body = body + '''\n'''
                    body = body + '''![image.png](/.attachments/''' + str(screenshot["filename"]) + ''')'''
                    body = body + '''\n'''
                    body = body + '''\n'''

        self.azureObj.createOrUpdatePage(wikiPagePath, body)

        self.status = "Created Azure page"
        self.progress = 100