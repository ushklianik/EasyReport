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

from app.backend.reporting.reporting_base         import ReportingBase
from app.backend.integrations.main.atlassian_jira import AtlassianJira
from datetime                                     import datetime


class AtlassianJiraReport(ReportingBase):

    def __init__(self, project):
        super().__init__(project)
        self.report_body = ""
        self.issue_id    = None

    def set_template(self, template):
        super().set_template(template)
        self.output_obj = AtlassianJira(project=self.project, name=self.output)

    def add_group_text(self, text):
        text += f'\n\n'
        return text

    def add_text(self, text):
        text = self.replace_variables(text)
        text += f'\n\n'
        return text

    def add_graph(self, name, current_run_id, baseline_run_id):
        image = self.grafana_obj.render_image(name, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        filename = self.output_obj.put_image_to_jira(issue=self.issue_id, image_bytes=image)
        if(filename):
            graph = f'!{str(filename)}|width=900!\n\n'
        else:
            graph = f'Image failed to load, name: {name}'
        return graph

    def generate_path(self, isgroup):
        if isgroup: title = self.group_title
        else: title = self.replace_variables(self.title)
        return title

    def create_issue(self, issue_title):
        self.issue_id = self.output_obj.put_page_to_jira(title=issue_title)
        return self.issue_id

    def generate_report(self, tests, template_group=None):
        templates_title = ""
        group_title = None
        def process_test(test, isgroup):
            nonlocal templates_title
            nonlocal group_title
            template_id = test.get('template_id')
            if template_id:
                self.set_template(template_id)
                run_id = test.get('runId')
                baseline_run_id = test.get('baseline_run_id')
                if not self.issue_id:
                    if isgroup:
                        group_title = self.generate_path(True)
                        self.create_issue(group_title)
                    else:
                        temporary_title = self.generate_path(False)
                        self.create_issue(temporary_title)
                title = self.generate_path(False)
                self.report_body += self.add_text(title)
                self.report_body += self.generate(run_id, baseline_run_id)
                if not group_title: templates_title += f'{title} | '
        if template_group:
            self.set_template_group(template_group)
            title = self.generate_path(True)
            self.report_body += self.add_group_text(title)
            for obj in self.template_order:
                if obj["type"] == "text":
                    self.report_body += self.add_group_text(obj["content"])
                elif obj["type"] == "template":
                    for test in tests:
                        if obj.get('content') == test.get('template_id'):
                            process_test(test, True)
        else:
            for test in tests:
                process_test(test, False)
        current_time = datetime.now()
        time_str = current_time.strftime("%d.%m.%Y %H:%M")
        if not group_title:
            templates_title += time_str
            self.output_obj.update_jira_page(self.issue_id, templates_title, self.report_body)
        else:
            group_title += f' {time_str}'
            self.output_obj.update_jira_page(self.issue_id, group_title, self.report_body)
        return self.report_body

    def generate(self, current_run_id, baseline_run_id = None):
        self.collect_data(current_run_id, baseline_run_id)
        report_body = ""
        for obj in self.data:
            if obj["type"] == "text":
                report_body += self.add_text(obj["content"])
            elif obj["type"] == "graph":
                report_body += self.add_graph(obj["content"], current_run_id, baseline_run_id)
        return report_body