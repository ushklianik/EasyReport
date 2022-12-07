from influxdb_client import InfluxDBClient, Point, Dialect
from influxdb_client.client.write_api import SYNCHRONOUS
from app.backend import tools
from app.backend.influxdb import custom
import logging
import pandas as pd
import json
import plotly
import plotly.express

def connectToInfluxDB(project):
    try:
        path  = tools.getDefaultInfluxdb(project)
        url   = tools.getValueFromYaml(path, "influxdbUrl")
        org   = tools.getValueFromYaml(path, "influxdbOrg")
        token = tools.getValueFromYaml(path, "influxdbToken")
        global influxdbClient
        influxdbClient = InfluxDBClient(url=url, org=org, token=token)
        global write_api
        write_api = influxdbClient.write_api(write_options=SYNCHRONOUS)
        global query_api
        query_api = influxdbClient.query_api()
        global delete_api
        delete_api = influxdbClient.delete_api()
    except Exception as er:
        logging.warning('ERROR: connection to influxdb failed')
        logging.warning(er)

def closeInfluxdbConnection():
    try:
        global influxdbClient
        influxdbClient.__del__()
    except Exception as er:
        logging.warning('ERROR: influxdb connection closing failed')
        logging.warning(er)



def getTestLog(project):
    connectToInfluxDB(project)
    result = []
    tables = query_api.query(custom.getTestLog)
    for table in tables:
        for row in table.records:
            del row.values["result"]
            del row.values["table"]
            result.append(row.values)
    return result

def getRT(runId):
    path  = tools.getDefaultInfluxdb("default")
    url   = tools.getValueFromYaml(path, "influxdbUrl")
    org   = tools.getValueFromYaml(path, "influxdbOrg")
    token = tools.getValueFromYaml(path, "influxdbToken")
    influxdbClient = InfluxDBClient(url=url, org=org, token=token)
    query_api = influxdbClient.query_api()
    result = query_api.query(custom.getResTime)
    for table in result:
        x_vals = []
        y_vals = []
        label = ""
        for record in table:
            y_vals.append(record["_value"])
            x_vals.append(record["_time"])
            #label = record["_measurement"]

    # Creating the Figure instance
    fig = plotly.express.line(x=x_vals, y=y_vals) 
    fig.update_layout(showlegend=False, 
                    paper_bgcolor = 'rgb(47, 46, 46)', 
                    plot_bgcolor = 'rgb(47, 46, 46)',
                    title_text='Response time',
                    title_font_color="white",
                    title_x=0.5
                    )
    fig.update_yaxes(gridcolor='#444444', color="white", title_text='Milliseconds', ticksuffix="ms")
    fig.update_xaxes(gridcolor='#444444', color="white", title_text='Time')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
            



