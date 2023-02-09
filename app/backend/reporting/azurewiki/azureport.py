from app.backend import pkg
from app.backend.grafana.grafana import grafana
from app.backend.influxdb.influxdb import influxdb
from app.backend.azure.azure import azure
import re

class azureport:

    def __init__(self, project, reportName):
        self.project        = project
        self.reportName     = reportName
        self.setConfig()
        self.grafanaObj     = grafana(project=self.project, name=self.grafanaName)
        self.influxdbObj    = influxdb(project=self.project, name=self.influxdbName)
        self.azureObj       = azure(project=self.project, name=self.outputName)
        self.progress       = 0
        self.status         = "Not started"

    def setConfig(self):
        config = pkg.getFlowConfigValues(self.project, self.reportName)
        self.influxdbName = config["influxdbName"]
        self.grafanaName  = config["grafanaName"]
        self.outputName   = config["outputName"]  
        self.graphs       = config["graphs"]
        self.footer       = config["footer"]
        self.header       = config["header"]
    
    def generateReport(self, current_runId, baseline_runId = None):
        self.influxdbObj.connectToInfluxDB()

        self.current_startTimeInflux    = self.influxdbObj.getStartTime(current_runId)
        self.current_endTimeInflux      = self.influxdbObj.getEndTime(current_runId)
        self.current_startTimestamp     = self.influxdbObj.getStartTmp(current_runId)
        self.current_endTimestamp       = self.influxdbObj.getEndTmp(current_runId)
        self.testName                   = self.influxdbObj.getTestName(current_runId, self.current_startTimeInflux, self.current_endTimeInflux)

        self.parameters = {}
        self.parameters["testName"]                 = self.testName

        self.parameters["current_startTime"]        = self.influxdbObj.getHumanStartTime(current_runId)
        self.parameters["current_endTime"]          = self.influxdbObj.getHumanEndTime(current_runId)
        self.parameters["current_grafanaLink"]      = self.grafanaObj.getGrafanaTestLink(self.current_startTimestamp, self.current_endTimestamp, self.testName, current_runId)
        self.parameters["current_duration"]         = str(int((self.current_endTimestamp - self.current_startTimestamp)/1000))
        self.parameters["current_vusers"]           = self.influxdbObj.getMaxActiveUsers(current_runId, self.current_startTimeInflux, self.current_endTimeInflux)
        
        if baseline_runId != None:
            self.baseline_startTimeInflux           = self.influxdbObj.getStartTime(baseline_runId)
            self.baseline_endTimeInflux             = self.influxdbObj.getEndTime(baseline_runId)
            self.baseline_startTimestamp            = self.influxdbObj.getStartTmp(baseline_runId)
            self.baseline_endTimestamp              = self.influxdbObj.getEndTmp(baseline_runId)

            self.parameters["baseline_startTime"]   = self.influxdbObj.getHumanStartTime(baseline_runId)
            self.parameters["baseline_endTime"]     = self.influxdbObj.getHumanEndTime(baseline_runId)
            self.parameters["baseline_grafanaLink"] = self.grafanaObj.getGrafanaTestLink(self.baseline_startTimestamp, self.baseline_endTimestamp, self.testName, baseline_runId)
            self.parameters["baseline_duration"]    = str(int((self.baseline_endTimestamp - self.baseline_startTimestamp)/1000))
            self.parameters["baseline_vusers"]      = self.influxdbObj.getMaxActiveUsers(baseline_runId, self.baseline_startTimeInflux, self.baseline_endTimeInflux)

        self.status = "Collected data from InfluxDB"
        self.progress = 25

        screenshots = self.grafanaObj.renderImageEncoded(self.graphs, self.current_startTimestamp, self.current_endTimestamp, self.testName, current_runId)
        self.status = "Rendered images in Grafana"
        self.progress = 50

        for screenshot in screenshots:
            fileName = self.azureObj.putImageToAzure(screenshot["image"], screenshot["name"])
            screenshot["filename"] = fileName

        self.status = "Uploaded images to Azure"
        self.progress = 75

        wikiPageName = str(self.parameters["current_vusers"]) + " users | Azure candidate | " + self.parameters["current_startTime"]
        wikiPagePath = self.azureObj.getPath() + "/" + self.testName + "/" + wikiPageName
        
        variables = re.findall(r"\$\{(.*?)\}", self.header)
        for var in variables:
            self.header = self.header.replace("${"+var+"}", str(self.parameters[var]))
        
        variables = re.findall(r"\$\{(.*?)\}", self.footer)
        for var in variables:
            self.footer = self.footer.replace("${"+var+"}", str(self.parameters[var]))
     
        body = self.header

        for idx in range(len(screenshots)):
            for screenshot in screenshots:
                if idx == screenshot["position"]:
                    body = body + '''\n'''
                    body = body + '''## ''' + str(screenshot["name"])
                    body = body + '''\n'''
                    body = body + '''![image.png](/.attachments/''' + str(screenshot["filename"]) + ''')'''
                    body = body + '''\n'''
                    body = body + '''\n'''

        body += self.footer

        self.azureObj.createOrUpdatePage(wikiPagePath, body)

        self.status = "Created Azure page"
        self.progress = 100