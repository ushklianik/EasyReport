from app.backend.influxdb import influxdb, custom
from datetime import datetime
from dateutil import tz
import plotly
import plotly.express
import json

class htmlReport:
    def __init__(self, project, runId):
        self.project = project
        self.runId = runId
        self.influxdbClient = influxdb.connectToInfluxDB(project)
        self.queryApi = self.influxdbClient.query_api()
        self.report = {}
        self.report['runId'] = runId
        self.report['stats'] = {}
        self.report['graph'] = {}
        self.tmz = tz.tzlocal()
    
    def getStartTime(self):
        fluxTables = self.queryApi.query(custom.getStartTime(self.runId))
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                self.report["startTimeStamp"] = datetime.strftime(fluxRecord['_time'],"%Y-%m-%dT%H:%M:%SZ")                   
                self.report["startTime"] = datetime.strftime(fluxRecord['_time'].astimezone(self.tmz), "%Y-%m-%d %I:%M:%S %p")    

    def getEndTime(self):
        fluxTables = self.queryApi.query(custom.getEndTime(self.runId))
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                self.report["endTimeStamp"] = datetime.strftime(fluxRecord['_time'],"%Y-%m-%dT%H:%M:%SZ")                 
                self.report["endTime"] = datetime.strftime(fluxRecord['_time'].astimezone(self.tmz), "%Y-%m-%d %I:%M:%S %p")  

    def getDuration(self):
        duration = datetime.strptime(self.report['endTimeStamp'], "%Y-%m-%dT%H:%M:%SZ") - datetime.strptime(self.report['startTimeStamp'], "%Y-%m-%dT%H:%M:%SZ")  
        self.report["duration"] = str(duration)
    
    def getMaxActiveUsers_stats(self):
        fluxTables = self.queryApi.query(custom.getMaxActiveUsers_stats(self.runId, self.report['startTimeStamp'], self.report['endTimeStamp']))
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                self.report['stats']['maxActiveThreads'] = fluxRecord['_value']
    
    def getAverageRPS_stats(self):
        fluxTables = self.queryApi.query(custom.getAverageRPS_stats(self.runId, self.report['startTimeStamp'], self.report['endTimeStamp']))
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                self.report['stats']['rps'] = round(fluxRecord['_value'], 2)
    
    def getErrorsPerc_stats(self):
        fluxTables = self.queryApi.query(custom.getErrorsPerc_stats(self.runId, self.report['startTimeStamp'], self.report['endTimeStamp']))
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                self.report['stats']['errors'] = round(fluxRecord['_value'], 2)
    
    def getAvgResponseTime_stats(self):
        fluxTables = self.queryApi.query(custom.getAvgResponseTime_stats(self.runId, self.report['startTimeStamp'], self.report['endTimeStamp']))
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                self.report['stats']['avgResponseTime'] = round(fluxRecord['_value'], 2)
    
    def get90ResponseTime_stats(self):
        fluxTables = self.queryApi.query(custom.get90ResponseTime_stats(self.runId, self.report['startTimeStamp'], self.report['endTimeStamp']))
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                self.report['stats']['percentileResponseTime'] = round(fluxRecord['_value'], 2)
    
    def getAvgBandwidth_stats(self):
        fluxTables = self.queryApi.query(custom.getAvgBandwidth_stats(self.runId, self.report['startTimeStamp'], self.report['endTimeStamp']))
        for fluxTable in fluxTables:
            for fluxRecord in fluxTable:
                self.report['stats']['avgBandwidth'] = round(fluxRecord['_value']/1048576, 2)

    def getAvgResponseTime_graph(self):
        fluxTables = self.queryApi.query(custom.getAvgResponseTime_graph(self.runId, self.report['startTimeStamp'], self.report['endTimeStamp']))
        for fluxTable in fluxTables:
            x_vals = []
            y_vals = []
            for fluxRecord in fluxTable:
                y_vals.append(fluxRecord["_value"])
                x_vals.append(fluxRecord["_time"])
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

        self.report['graph']['avgResponseTime'] = json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    def getRPS_graph(self):
        fluxTables = self.queryApi.query(custom.getRPS_graph(self.runId, self.report['startTimeStamp'], self.report['endTimeStamp']))
        for fluxTable in fluxTables:
            x_vals = []
            y_vals = []
            for fluxRecord in fluxTable:
                y_vals.append(fluxRecord["_value"])
                x_vals.append(fluxRecord["_time"])
        fig = plotly.express.line(x=x_vals, y=y_vals) 
        fig.update_layout(showlegend=False, 
                    paper_bgcolor = 'rgb(47, 46, 46)', 
                    plot_bgcolor = 'rgb(47, 46, 46)',
                    title_text='RPS',
                    title_font_color="white",
                    title_x=0.5
                    )
        fig.update_yaxes(gridcolor='#444444', color="white", title_text='r/s', ticksuffix="r/s")
        fig.update_xaxes(gridcolor='#444444', color="white", title_text='Time')

        self.report['graph']['rps'] = json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    
    def createReport(self):
        self.getStartTime()
        self.getEndTime()
        self.getDuration()
        self.getMaxActiveUsers_stats()
        self.getAverageRPS_stats()
        self.getErrorsPerc_stats()
        self.getAvgResponseTime_stats()
        self.get90ResponseTime_stats()
        self.getAvgBandwidth_stats()
        self.getAvgResponseTime_graph()
        self.getRPS_graph()
        influxdb.closeInfluxdbConnection(self.influxdbClient)