from os import path
from app.backend import pkg
import os
import json

class azure:
    def __init__(self, project, name = None):
        self.project                    = project
        self.path                       = "./app/projects/" + project + "/config.json"
        self.setConfig(name)
    
    def setConfig(self, name):
        if path.isfile(self.path) is False or os.path.getsize(self.path) == 0:
            return {"status":"error", "message":"No config.json"}
        else:   
            if name == None:
                name = pkg.getDefaultAzure(self.project)
            with open(self.path, 'r') as fp:
                fl = json.load(fp)
                for config in fl["integrations"]["azure"]:
                    if config['name'] == name:
                        self.name                 = config["name"]
                        self.personalAccessToken  = config["personalAccessToken"]
                        self.wikiOrganizationUrl  = config["wikiOrganizationUrl"]
                        self.wikiProject          = config["wikiProject"]
                        self.wikiIdentifier       = config["wikiIdentifier"]
                        self.wikiPathToReport     = config["wikiPathToReport"]
                        self.appInsighsLogsServer = config["appInsighsLogsServer"]
                        self.appInsighsAppId      = config["appInsighsAppId"]
                        self.appInsighsApiKey     = config["appInsighsApiKey"]
                    else:
                        return {"status":"error", "message":"No such config name"}