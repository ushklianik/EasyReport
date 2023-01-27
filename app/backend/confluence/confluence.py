from os import path
from app.backend import pkg
import os
import json
import requests
import base64
import logging
import random

class confluence:
    def __init__(self, project, name = None):
        self.project                    = project
        self.path                       = "./app/projects/" + project + "/config.json"
        self.setConfig(name)
    
    def setConfig(self, name):
        if path.isfile(self.path) is False or os.path.getsize(self.path) == 0:
            return {"status ":"error", "message":"No config.json"}
        else:   
            if name == None:
                name = pkg.getDefaultConfl(self.project)
            with open(self.path, 'r') as fp:
                fl = json.load(fp)
                for config in fl["integrations"]["conflwiki"]:
                    if config['name'] == name:
                        self.name                 = config["name"]
                        self.personalAccessToken  = config["personalAccessToken"]
                        self.wikiOrganizationUrl  = config["wikiOrganizationUrl"]
                        self.wikiParentId         = config["wikiParentId"]
                        self.wikiSpaceKey         = config["wikiSpaceKey"]
                        self.conflHeadersAttachments = {
                            'X-Atlassian-Token': 'nocheck',
                            'Content-Type': 'application/octet-stream',
                            'Authorization': f'Basic {config["personalAccessToken"]}'
                        }
                        self.conflAuthorizationHeaders = {
                                'Accept': 'application/json',
                                'Authorization': f'Basic {config["personalAccessToken"]}'
                        }
                    else:
                        return {"status":"error", "message":"No such config name"}