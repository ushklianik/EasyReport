from influxdb_client import InfluxDBClient, Point, Dialect
from influxdb_client.client.write_api import SYNCHRONOUS
from app.backend import tools
from app.backend.influxdb import custom
import logging
import pandas as pd
import json

def connectToInfluxDB(project):
    try:
        path  = tools.getDefaultInfluxdb(project)
        url   = tools.getValueFromYaml(path, "influxdbUrl")
        org   = tools.getValueFromYaml(path, "influxdbOrg")
        token = tools.getValueFromYaml(path, "influxdbToken")
        influxdbClient = InfluxDBClient(url=url, org=org, token=token)
        return influxdbClient
        # global write_api
        # write_api = influxdbClient.write_api(write_options=SYNCHRONOUS)
        # global query_api
        # query_api = influxdbClient.query_api()
        # global delete_api
        # delete_api = influxdbClient.delete_api()
    except Exception as er:
        logging.warning('ERROR: connection to influxdb failed')
        logging.warning(er)

def closeInfluxdbConnection(influxdbClient):
    try:
        influxdbClient.__del__()
    except Exception as er:
        logging.warning('ERROR: influxdb connection closing failed')
        logging.warning(er)



def getTestLog(project):
    influxdbClient = connectToInfluxDB(project)
    result = []
    tables = influxdbClient.query_api().query(custom.getTestLog)
    for table in tables:
        for row in table.records:
            del row.values["result"]
            del row.values["table"]
            result.append(row.values)
    closeInfluxdbConnection(influxdbClient)
    return result
            



