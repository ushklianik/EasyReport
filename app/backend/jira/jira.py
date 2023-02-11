from os import path
from app.backend import pkg
import os
import json
import requests
import base64
import logging
import random
from jira import JIRA

class jira:
    def __init__(self, project, name = None):
        self.project                    = project
        self.path                       = "./app/projects/" + project + "/config.json"
        self.setConfig(name)
    
    def setConfig(self, name):
        if path.isfile(self.path) is False or os.path.getsize(self.path) == 0:
            return {"status ":"error", "message":"No config.json"}
        else:   
            if name == None:
                name = pkg.getDefaultJira(self.project)
            config = pkg.getConflJiraConfigValues(self.project, name)
            if "name" in config:
                if config['name'] == name:
                    self.name                 = config["name"]
                    self.password             = config["password"]
                    self.jiraOrganizationUrl  = config["jiraOrganizationUrl"]
                    self.project              = config["project"]
                    self.epic                 = config["epic"]
                    self.email                = config["email"]
                    self.authjira                = JIRA(
                        basic_auth=(self.email, self.password),
                        options={'server': self.jiraOrganizationUrl}
                    )
                else:
                    return {"status":"error", "message":"No such config name"}

    def putPageToJira(self, title):
        issueDict = {
            'project': {'key': self.project},
            'summary': title,
            'issuetype': {'name': 'Task'},
            'customfield_14500': self.epic
        }
        try:
            jiraissue = self.authjira.create_issue(fields=issueDict)
            return jiraissue
        except Exception as er:
            logging.warning(er)
            return {"status":"error", "message":er}

    def putImageToJira(self, issue, image, filename):
        filename = filename.replace(" ", "-") + ".png"
        for i in range(3):
            try:
                self.authjira.add_attachment(issue, image, filename)
                return filename
            except Exception as er:
                print(er)
                logging.warning('ERROR: uploading image to Jira failed')
                logging.warning(er)

    def updateJiraPage(self, jiraissue, description):
        jiraissue.update(
            fields={"description": description}, json=True)