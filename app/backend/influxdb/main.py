from influxdb_client import InfluxDBClient
from app.backend import pkg
from app.backend.influxdb import custom
import logging


class influxdb:
    def __init__(self, project):
        self.project = project
        self.influxdbConnection = self.connectToInfluxDB()

    def connectToInfluxDB(self):
        try:
            configName   = pkg.getDefaultInfluxdb(self.project)
            influxdbConf = pkg.getInfluxdbConfigValues(self.project, configName)
            influxdbClient = InfluxDBClient(url=influxdbConf["influxdbUrl"], org=influxdbConf["influxdbOrg"], token=influxdbConf["influxdbToken"])
            return influxdbClient
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
    
    def getAppName(self, runId):
        fluxTables = self.influxdbConnection.query_api().query(query)
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                results.append(fluxRecord)
        return results
            



