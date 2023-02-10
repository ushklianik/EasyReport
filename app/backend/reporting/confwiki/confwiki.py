from app.backend import pkg
from app.backend.grafana.grafana import grafana
from app.backend.influxdb.influxdb import influxdb
from app.backend.confluence.confluence import confluence
from datetime import datetime
import threading
import re

class confreport:

    def __init__(self, project, reportName):
        self.project        = project
        self.reportName     = reportName
        self.setConfig()
        self.grafanaObj     = grafana(project=self.project, name=self.grafanaName)
        self.influxdbObj    = influxdb(project=self.project, name=self.influxdbName)
        self.conflObj       = confluence(project=self.project, name=self.outputName)
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

            wikiPageName = str(self.parameters["current_vusers"]) + " users | " + self.parameters["current_startTime"]

            screenshots = self.grafanaObj.renderImage(self.graphs, self.current_startTimestamp, self.current_endTimestamp, self.testName, current_runId, baseline_runId)
            self.status = "Rendered images in Grafana"
            self.progress = 50

            response = self.conflObj.putPage(title=wikiPageName, content="")

            if "id" in response:
                for screenshot in screenshots:
                    fileName = self.conflObj.putImageToConfl(screenshot["image"], screenshot["name"], pageId=response["id"])
                    screenshot["filename"] = fileName

            self.status = "Uploaded images to Confluence"
            self.progress = 75

            # wikiPagePath = self.conflObj.getPath() + "/" + self.testName + "/" + wikiPageName
            
            variables = re.findall(r"\$\{(.*?)\}", self.header)
            for var in variables:
                if "Link" in var:
                    self.parameters[var] = self.parameters[var].replace("&","&amp;")    
                self.header = self.header.replace("${"+var+"}", str(self.parameters[var])) 
                        
            variables = re.findall(r"\$\{(.*?)\}", self.footer)
            for var in variables:
                if "Link" in var:
                    self.parameters[var] = self.parameters[var].replace("&","&amp;")   
                self.footer = self.footer.replace("${"+var+"}", str(self.parameters[var]))
        
            body = self.header

            for idx in range(len(screenshots)):
                for screenshot in screenshots:
                    if idx == screenshot["position"]:
                        body = body + '''\n'''
                        body = body + '''<h2>''' + str(screenshot["name"]) + '''</h2>'''
                        body = body + '''<ac:image ac:align="center" ac:layout="center" ac:original-width="1000"><ri:attachment ri:filename="''' + str(screenshot["filename"]) + '''" /></ac:image>'''

            body += self.footer

            self.conflObj.createOrUpdatePage(title=wikiPageName,content=body)

            self.status = "Created Confluence wiki page"
            self.progress = 100