from influxdb_client import InfluxDBClient
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
        self.tmz = tz.tzlocal()
        
    def setConfig(self, name):
        if path.isfile(self.path) is False or os.path.getsize(self.path) == 0:
            return {"status":"error", "message":"No config.json"}
        else:
            if name == None:
                name = pkg.getDefaultInfluxdb(self.project)
            with open(self.path, 'r') as fp:
                fl = json.load(fp)
                for config in fl["integrations"]["influxdb"]:
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
            print(self.influxdbUrl)
            influxdbClient = InfluxDBClient(url=self.influxdbUrl, org=self.influxdbOrg, token=self.influxdbToken)
            self.influxdbConnection = influxdbClient
            return self
        except Exception as er:
            logging.warning('ERROR: connection to influxdb failed')
            logging.warning(er)

    def closeInfluxdbConnection(self):
        try:
            self.influxdbConnection.__del__()
        except Exception as er:
            logging.warning('ERROR: influxdb connection closing failed')
            logging.warning(er)

    def getTestLog(self):
        result = []
        tables = self.influxdbConnection.query_api().query(custom.getTestLog)
        for table in tables:
            for row in table.records:
                del row.values["result"]
                del row.values["table"]
                result.append(row.values)
        return result

    def sendQuery(self, query):
        results = []
        fluxTables = self.influxdbConnection.query_api().query(query)
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                results.append(fluxRecord)
        return results

    def getHumanStartTime(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getStartTime(runId))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:               
                tmp = datetime.strftime(fluxRecord['_time'].astimezone(self.tmz), "%Y-%m-%d %I:%M:%S %p") 
        return tmp

    def getStartTime(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getStartTime(runId))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                tmp = datetime.strftime(fluxRecord['_time'].astimezone(self.tmz), "%Y-%m-%d %I:%M:%S %p")   
        return tmp

    def getHumanEndTime(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getEndTime(runId))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                tmp = datetime.strftime(fluxRecord['_time'].astimezone(self.tmz), "%Y-%m-%d %I:%M:%S %p")
        return tmp

    def getEndTime(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(custom.getEndTime(runId))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                tmp = datetime.strftime(fluxRecord['_time'],"%Y-%m-%dT%H:%M:%SZ")                 
        return tmp 

    def getMaxActiveUsers(self, runId, start, end):
        fluxTables = self.influxdbConnection.query_api().query(custom.getMaxActiveUsers_stats(runId, start, end))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                users = fluxRecord['_value'] 
        return users  

    # def getAppName(self, runId):
    #     fluxTables = self.influxdbConnection.query_api().query(query)
    #     for fluxTable in fluxTables:
    #         for fluxRecord in fluxTable:
    #             results.append(fluxRecord)
    #     return results
            



