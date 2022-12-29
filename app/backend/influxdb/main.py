from influxdb_client import InfluxDBClient
from app.backend import tools
from app.backend.influxdb import custom
import logging


class influxdb:
    def __init__(self, project):
        self.project = project
        self.influxdbConnection = self.connectToInfluxDB()

    def connectToInfluxDB(self):
        try:
            path  = tools.getDefaultInfluxdb(self.project)
            url   = tools.getValueFromYaml(path, "influxdbUrl")
            org   = tools.getValueFromYaml(path, "influxdbOrg")
            token = tools.getValueFromYaml(path, "influxdbToken")
            influxdbClient = InfluxDBClient(url=url, org=org, token=token)
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
            



