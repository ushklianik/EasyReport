from os import path
from app.backend import pkg
from app.backend.integrations.integration import integration
import os
import requests
import base64
import logging
import random

class azure(integration):
    def __init__(self, project, name = None):
        super().__init__(project)
        self.set_config(name)
    
    def set_config(self, name):
        if path.isfile(self.config_path) is False or os.path.getsize(self.config_path) == 0:
            return {"status":"error", "message":"No config.json"}
        else:   
            if name == None:
                name = pkg.get_default_azure(self.project)
            config = pkg.get_azure_config_values(self.project, name)
            if "name" in config:
                if config['name'] == name:
                    self.name                    = config["name"]
                    self.token                   = config["token"]
                    self.org_url                 = config["org_url"]
                    self.project_id              = config["project_id"]
                    self.identifier              = config["identifier"]
                    self.path_to_report          = config["path_to_report"]
                    self.azure_headers_attachments = {
                            'Accept': 'application/json',
                            'Authorization': 'Basic ' + str(base64.b64encode(bytes(':'+ self.token, 'ascii')), 'ascii'),
                            'Content-Type': 'application/octet-stream'
                        }
                    self.azure_authorization_headers = {
                            'Accept': 'application/json',
                            'Authorization': 'Basic ' + str(base64.b64encode(bytes(':'+ self.token, 'ascii')), 'ascii')
                        }
                else:
                    return {"status":"error", "message":"No such config name"}
    
    def get_path(self):
        return self.path_to_report
        
    def put_image_to_azure(self, image, name):
        name = name.replace(" ", "-") + ".png"
        for i in range(3):
            try:
                response = requests.put(
                url=self.org_url + "/" + self.project +"/_apis/wiki/wikis/"+self.identifier+"/attachments?name="+name+"&api-version=6.0", headers=self.azure_headers_attachments, data=image) 
                if response.status_code != 201:
                    name = str(random.randint(1,100)) + name
                elif response.status_code == 201:
                    return name
            except Exception as er:
                logging.warning('ERROR: uploading image to azure failed')
                logging.warning(er)   
    
    def put_page(self, path, page_content):
        wiki_api_url = self.org_url + "/"+self.project_id+"/_apis/wiki/wikis/"+self.identifier+"/pages?path="+path+"&api-version=6.0"
        try:
            response = requests.put(
                url=wiki_api_url, headers=self.azure_authorization_headers, json={ "content": page_content })
            return response
        except Exception as er:
            logging.warning('ERROR: failed to upload the page to wiki')
            logging.warning(er)

    def get_page(self, path):
        wiki_api_url = self.org_url + "/"+self.project_id+"/_apis/wiki/wikis/"+self.identifier+"/pages?path="+path+"&api-version=6.0"
        try:
            response = requests.get(url=wiki_api_url, headers=self.azure_authorization_headers)
            return response
        except Exception as er:
            logging.warning('ERROR: getting ETag failed')
            logging.warning(er)      

    def create_or_update_page(self, path, page_content):
        response = self.put_page(path, page_content)
        for x in range(1,5):
            if "WikiAncestorPageNotFoundException" in str(response.content):
                newPage = '/'.join(path.split('/')[:-x])
                response = self.put_page(newPage, '')
            else:
                response = self.put_page(path, page_content)
                break
        if "specified in the add operation already exists in the wiki" in str(response.content):
            try:
                response = self.get_page(path)
            except Exception as er:
                logging.warning('ERROR: getting ETag failed')
                logging.warning(er)       
            self.azure_authorization_headers["If-Match"]=str(response.headers["ETag"])
            try:
                response = self.put_page(path, page_content)
            except Exception as er:
                logging.warning('ERROR: failed to update the page in wiki')
                logging.warning(er)  