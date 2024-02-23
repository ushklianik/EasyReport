# Copyright 2023 Uladzislau Shklianik <ushklianik@gmail.com> & Siamion Viatoshkin <sema.cod@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import os
import logging
import uuid

from app.backend                          import pkg
from app.backend.integrations.integration import Integration
from atlassian                            import Jira
from os                                   import path


class AtlassianJira(Integration):

    def __init__(self, project, name = None):
        super().__init__(project)
        self.set_config(name)

    def __str__(self):
        return f'Integration name is {self.name}, url is {self.org_url}'

    def set_config(self, name):
        if path.isfile(self.config_path) is False or os.path.getsize(self.config_path) == 0:
            return {"status":"error", "message":"No config.json"}
        else:
            if name == None:
                name = pkg.get_default_atlassian_jira(self.project)
            config = pkg.get_atlassian_jira_config_values(self.project, name)
            if "name" in config:
                if config['name'] == name:
                    self.name             = config["name"]
                    self.email            = config["email"]
                    self.token            = config["token"]
                    self.token_type       = config["token_type"]
                    self.org_url          = config["org_url"]
                    self.project_id       = config["project_id"]
                    self.epic_field       = config["epic_field"]
                    self.epic_name        = config["epic_name"]
                    if self.token_type == "api_token":
                        self.jira_auth = Jira(
                            url      = self.org_url,
                            username = self.email,
                            password = self.token
                        )
                    elif self.token_type == "personal_access_token":
                        self.jira_auth = Jira(
                            url   = self.org_url,
                            token = self.token
                        )
                    else:
                        return {"status":"error", "message":"No such token type name"}
                else:
                    return {"status":"error", "message":"No such config name"}

    def put_page_to_jira(self, title):
        issue_dict = {
            'project': {'key': self.project_id},
            'summary': title,
            'issuetype': {'name': 'Task'},
            self.epic_field: self.epic_name
        }
        try:
            jira_issue = self.jira_auth.issue_create(fields=issue_dict)
            return jira_issue['key']
        except Exception as er:
            logging.warning(er)
            return {"status":"error", "message":er}

    def put_image_to_jira(self, issue, image_bytes):
        filename = f'{uuid.uuid4()}.png'
        attachment = io.BytesIO(image_bytes)
        attachment.name = filename
        for i in range(3):
            try:
                self.jira_auth.add_attachment_object(issue_key=issue, attachment=attachment)
                return filename
            except Exception as er:
                logging.warning('ERROR: uploading image to Jira failed')
                logging.warning(er)

    def update_jira_page(self, issue, title, description):
        fields_dict = {
            'summary': title,
            'description': description
        }
        try:
            update = self.jira_auth.issue_update(issue_key=issue, fields=fields_dict)
            return update
        except Exception as er:
                logging.warning('ERROR: updating Jira issue failed')
                logging.warning(er)