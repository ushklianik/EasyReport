from os import path
from app.backend import pkg
from app.backend.integrations.integration import integration
from jira import JIRA
import os
import logging


class jira(integration):
    def __init__(self, project, name = None):
        super().__init__(project)
        self.set_config(name)
    
    def set_config(self, name):
        if path.isfile(self.config_path) is False or os.path.getsize(self.config_path) == 0:
            return {"status ":"error", "message":"No config.json"}
        else:   
            if name == None:
                name = pkg.get_default_atlassian_jira(self.project)
            config = pkg.get_atlassian_jira_config_values(self.project, name)
            if "name" in config:
                if config['name'] == name:
                    self.name             = config["name"]
                    self.token            = config["token"]
                    self.org_url          = config["org_url"]
                    self.project_id       = config["project_id"]
                    self.epic             = config["epic"]
                    self.email            = config["email"]
                    self.auth_jira        = JIRA(
                        basic_auth=(self.email, self.token),
                        options={'server': self.org_url}
                    )
                else:
                    return {"status":"error", "message":"No such config name"}

    def put_page_to_jira(self, title):
        issue_dict = {
            'project': {'key': self.project},
            'summary': title,
            'issuetype': {'name': 'Task'},
            'customfield_14500': self.epic
        }
        try:
            jira_issue = self.auth_jira.create_issue(fields=issue_dict)
            return jira_issue
        except Exception as er:
            logging.warning(er)
            return {"status":"error", "message":er}

    def put_image_to_jira(self, issue, image, filename):
        filename = filename.replace(" ", "-") + ".png"
        for i in range(3):
            try:
                self.auth_jira.add_attachment(issue, image, filename)
                return filename
            except Exception as er:
                print(er)
                logging.warning('ERROR: uploading image to Jira failed')
                logging.warning(er)

    def update_jira_page(self, jira_issue, description):
        jira_issue.update(
            fields={"description": description}, json=True)