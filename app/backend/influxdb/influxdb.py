from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from app.backend import pkg
from app.backend.influxdb import custom
import logging
import json
from os import path
import os
from datetime import datetime
from dateutil import tz


class influxdb:
    def __init__(self, project, name = None):
        self.project              = project
        self.path                 = "./app/projects/" + project + "/config.json"
        self.setConfig(name)
        self.tmz = tz.tzutc()
        
    def setConfig(self, name):
        if path.isfile(self.path) is False or os.path.getsize(self.path) == 0:
            return {"status":"error", "message":"No config.json"}
        else:
            if name == None:
                name = pkg.getDefaultInfluxdb(self.project)
            config = pkg.getInfluxdbConfigValues(self.project, name)
            if "name" in config:
                if config['name'] == name:
                    self.name                = config["name"]
                    self.influxdbUrl         = config["influxdbUrl"]
                    self.influxdbOrg         = config["influxdbOrg"]
                    self.influxdbToken       = config["influxdbToken"]
                    self.influxdbTimeout     = config["influxdbTimeout"]
                    self.influxdbBucket      = config["influxdbBucket"]
                    self.influxdbMeasurement = config["influxdbMeasurement"]
                    self.influxdbField       = config["influxdbField"]
                    self.influxdbTestIdTag   = config["influxdbTestIdTag"]
                    if config["isDefault"] != None:
                        self.isDefault       = config["isDefault"]
                    else:
                        self.isDefault       = "n"

    def connectToInfluxDB(self):
        try:
            influxdbClient = InfluxDBClient(url=self.influxdbUrl, org=self.influxdbOrg, token=self.influxdbToken)
            self.influxdbConnection = influxdbClient
            msg = {"status":"created", "message":""}
        except Exception as er:
            logging.warning(er)
            msg = {"status":"error", "message":er}
        return self

    def closeInfluxdbConnection(self):
        try:
            self.influxdbConnection.__del__()
        except Exception as er:
            logging.warning('ERROR: influxdb connection closing failed')
            logging.warning(er)

    def getTestLog(self):
        result = []
        try:
            tables = self.influxdbConnection.query_api().query(custom.getTestLogQuery(self.influxdbBucket))
            for table in tables:
                for row in table.records:
                    del row.values["result"]
                    del row.values["table"]
                    result.append(row.values)
            msg = {"status":"good", "message":result}
            print(msg)
        except Exception as er:
            logging.warning(er)
            msg = {"status":"error", "message":er}
            print(msg)
        return msg

    def sendQuery(self, query):
        results = []
        fluxTables = self.influxdbConnection.query_api().query(query)
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                results.append(fluxRecord)
        return results
    
    def writePoint(self, point):
        self.influxdbConnection.write_api(write_options=SYNCHRONOUS).write(bucket=self.influxdbBucket, org=self.influxdbOrg, record=point)

    def getHumanStartTime(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getStartTime(runId, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:               
                tmp = datetime.strftime(fluxRecord['_time'].astimezone(self.tmz), "%Y-%m-%d %I:%M:%S %p") 
        return tmp

    def getStartTime(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getStartTime(runId, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                tmp = datetime.strftime(fluxRecord['_time'],"%Y-%m-%dT%H:%M:%SZ") 
        return tmp

    def getStartTmp(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getStartTime(runId, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                tmp = int(fluxRecord['_time'].astimezone(self.tmz).timestamp() * 1000)
        return tmp

    def getEndTmp(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getEndTime(runId, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                tmp = int(fluxRecord['_time'].astimezone(self.tmz).timestamp() * 1000)
        return tmp

    def getHumanEndTime(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getEndTime(runId, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                tmp = datetime.strftime(fluxRecord['_time'].astimezone(self.tmz), "%Y-%m-%d %I:%M:%S %p")
        return tmp

    def getEndTime(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getEndTime(runId, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                tmp = datetime.strftime(fluxRecord['_time'],"%Y-%m-%dT%H:%M:%SZ")                 
        return tmp 

    def getMaxActiveUsers(self, runId, start, end):
        fluxTables = self.influxdbConnection.query_api().query(custom.getMaxActiveUsers_stats(runId, start, end, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                users = fluxRecord['_value'] 
        return users  

    def getTestName(self, runId, start, end):
        fluxTables = self.influxdbConnection.query_api().query(custom.getAppName(runId, start, end, self.influxdbBucket))
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                appName = fluxRecord['testName']
        return appName

    def addOrUpdateTest(self, runId, status, build, testName):
        fluxTables = self.influxdbConnection.query_api().query(custom.getTestNames(runId, self.influxdbBucket))
        isTestExist = False
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                if runId == fluxRecord["runId"]:
                    isTestExist = True
        if isTestExist:
            self.deleteTestData("tests", runId)
            self.addBaseline(runId, status, build, testName)
        else:
            self.addBaseline(runId, status, build, testName)

    def deleteTestData(self, measurement, runId, start = None, end = None):
        if start == None: start = "2000-01-01T00:00:00Z"
        else: 
            start = datetime.strftime(datetime.fromtimestamp(int(start)/1000).astimezone(self.tmz),"%Y-%m-%dT%H:%M:%SZ")
        if end   == None: end = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        else: 
            end = datetime.strftime(datetime.fromtimestamp(int(end)/1000).astimezone(self.tmz),"%Y-%m-%dT%H:%M:%SZ")
        try:
            print(start)
            print(end)
            self.influxdbConnection.delete_api().delete(start, end, '_measurement="'+measurement+'" AND runId="'+runId+'"',bucket=self.influxdbBucket, org=self.influxdbOrg)
        except Exception as er:
            logging.warning('ERROR: deleteTestPoint method failed')
            logging.warning(er)
    
    def getMaxActiveUsers_stats(self, runId, start, end):
        fluxTables = self.influxdbConnection.query_api().query(custom.getMaxActiveUsers_stats(runId, start, end, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                value = fluxRecord['_value']
        return value
    
    def getAverageRPS_stats(self, runId, start, end):
        fluxTables = self.influxdbConnection.query_api().query(custom.getAverageRPS_stats(runId, start, end, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                value = round(fluxRecord['_value'], 2)
        return value
    
    def getErrorsPerc_stats(self, runId, start, end):
        fluxTables = self.influxdbConnection.query_api().query(custom.getErrorsPerc_stats(runId, start, end, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                value = round(fluxRecord['_value'], 2)
        return value
    
    def getAvgResponseTime_stats(self, runId, start, end):
        fluxTables = self.influxdbConnection.query_api().query(custom.getAvgResponseTime_stats(runId, start, end, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                value = round(fluxRecord['_value'], 2)
        return value
    
    def get90ResponseTime_stats(self, runId, start, end):
        fluxTables = self.influxdbConnection.query_api().query(custom.get90ResponseTime_stats(runId, start, end, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                value = round(fluxRecord['_value'], 2)
        return value
    
    def getMedianResponseTime_stats(self, runId, start, end):
        fluxTables = self.influxdbConnection.query_api().query(custom.getMedianResponseTime_stats(runId, start, end, self.influxdbBucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                value = round(fluxRecord['_value'], 2)
        return value

    def addBaseline(self, runId, status, build, testName):
        self.connectToInfluxDB()
        start_time         = self.getHumanStartTime(runId)
        end_time           = self.getHumanEndTime(runId)
        start_time_infl    = self.getStartTime(runId)
        end_time_infl      = self.getEndTime(runId)
        avg_tr             = self.getAvgResponseTime_stats(runId, start_time_infl, end_time_infl)
        percentile_tr      = self.get90ResponseTime_stats(runId, start_time_infl, end_time_infl)
        median_tr          = self.getMedianResponseTime_stats(runId, start_time_infl, end_time_infl)
        try:
            p = Point("tests").tag("runId", runId) \
                    .tag("startTime", start_time).tag("endTime", end_time) \
                    .tag("testName", testName).tag("status", status) \
                    .tag("build", build) \
                    .field("median_tr", median_tr) \
                    .field("avg_tr", avg_tr) \
                    .field("percentile_tr", percentile_tr)
            self.writePoint(p)
        except Exception as er:
            logging.warning('ERROR: baseline stats uploading failed')
            logging.warning(er)