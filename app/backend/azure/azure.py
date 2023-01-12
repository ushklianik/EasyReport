from os import path
from app.backend import pkg
import os
import json
import requests
import base64
import logging
import random

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
                        self.azureHeadersAttachments = {
                                'Accept': 'application/json',
                                'Authorization': 'Basic ' + str(base64.b64encode(bytes(':'+ self.personalAccessToken, 'ascii')), 'ascii'),
                                'Content-Type': 'application/octet-stream'
                            }
                        self.azureAuthorizationHeaders = {
                                'Accept': 'application/json',
                                'Authorization': 'Basic ' + str(base64.b64encode(bytes(':'+ self.personalAccessToken, 'ascii')), 'ascii')
                            }
                    else:
                        return {"status":"error", "message":"No such config name"}

    def getPath(self):
        return self.wikiPathToReport
        
    def putImageToAzure(self, image, name):
        name = name.replace(" ", "-") + ".png"
        for i in range(3):
            try:
                response = requests.put(
                url=self.wikiOrganizationUrl + "/" + self.wikiProject +"/_apis/wiki/wikis/"+self.wikiIdentifier+"/attachments?name="+name+"&api-version=6.0", headers=self.azureHeadersAttachments, data=image)
            except Exception as er:
                logging.warning('ERROR: uploading image to azure failed')
                logging.warning(er)    
            if response.status_code != 201:
                name = str(random.randint(1,100)) + name
            elif response.status_code == 201:
                return name
    
    def putPage(self, path, pageContent):
        wiki_api_url = self.wikiOrganizationUrl + "/"+self.wikiProject+"/_apis/wiki/wikis/"+self.wikiIdentifier+"/pages?path="+path+"&api-version=6.0"
        try:
            response = requests.put(
                url=wiki_api_url, headers=self.azureAuthorizationHeaders, json={ "content": pageContent })
            return response
        except Exception as er:
            logging.warning('ERROR: failed to upload the page to wiki')
            logging.warning(er)
    
    def getPage(self, path):
        wiki_api_url = self.wikiOrganizationUrl + "/"+self.wikiProject+"/_apis/wiki/wikis/"+self.wikiIdentifier+"/pages?path="+path+"&api-version=6.0"
        try:
            response = requests.get(url=wiki_api_url, headers=self.azureAuthorizationHeaders)
            return response
        except Exception as er:
            logging.warning('ERROR: getting ETag failed')
            logging.warning(er)      
    
    def createOrUpdatePage(self, path, pageContent):

        response = self.putPage(path, pageContent)
        for x in range(1,5):
            if "WikiAncestorPageNotFoundException" in str(response.content):
                newPage = '/'.join(path.split('/')[:-x])
                response = self.putPage(newPage, '')
            else:
                response = self.putPage(path, pageContent)
                break

        if "specified in the add operation already exists in the wiki" in str(response.content):
            try:
                response = self.getPage(path)
            except Exception as er:
                logging.warning('ERROR: getting ETag failed')
                logging.warning(er)       
            self.azureAuthorizationHeaders["If-Match"]=str(response.headers["ETag"])
            try:
                response = self.putPage(path, pageContent)
            except Exception as er:
                logging.warning('ERROR: failed to update the page in wiki')
                logging.warning(er)  