from app.backend import pkg
from app.backend.reporting.reporting_base import reporting_base
from app.backend.integrations.atlassian.jira import jira
from datetime import datetime
from html import escape
import re

class atlassian_jira_report(reporting_base):

    def __init__(self, project, template):
        super().__init__(project, template)
        self.output_obj  = jira(project=self.project, name=self.output)
        self.report_body = ""
        self.issue_id    = None

    def add_text(self, text):
        text = self.replace_variables(text)
        text += '''\n'''
        text += '''\n'''
        text = text.replace('\\"', '"')
        text = text.replace('&', '&amp;')
        return text
    
    def add_graph(self, name, current_run_id, baseline_run_id):
        image = self.grafana_obj.render_image(name, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        fileName = self.output_obj.put_image_to_jira(issue=self.issue_id, image_bytes=image, filename=name, test_id=current_run_id)
        if(fileName):
            graph = '''!''' + str(fileName) + '''|width=1000,height=500!'''
        else:
            graph = 'Image failed to load, name: '+ name
        graph = graph + '''\n'''
        graph = graph + '''\n'''
        return graph

    def generate_path(self):
        title = self.replace_variables(self.title)
        return title

    def create_issue(self):
        path = self.generate_path()
        jira_issue = self.output_obj.put_page_to_jira(title=path)
        self.issue_id=jira_issue

    def generate_report(self, tests):
        if len(tests) == 2: 
            self.report_body += self.generate(current_run_id=tests[0], baseline_run_id=tests[-1])
        elif(len(tests) == 0):
            return "Please provide for which tests you need to make a report"
        else:
            for test in tests:
                self.report_body += self.generate(current_run_id=test)
        self.output_obj.update_jira_page(self.issue_id, self.report_body)
        return self.report_body

    def generate(self, current_run_id, baseline_run_id = None):
        self.collect_data(current_run_id, baseline_run_id)
        if not self.issue_id:
           self.create_issue()
        report_body = ""
        for obj in self.data:
            if obj["type"] == "text":
                report_body += self.add_text(obj["content"])
            elif obj["type"] == "graph":
                report_body += self.add_graph(obj["content"], current_run_id, baseline_run_id)
            elif obj["type"] == "template":
                for sub_obj in self.get_template_data(obj["content"]):
                    if sub_obj["type"] == "text":
                        report_body += self.add_text(sub_obj["content"])
                    elif sub_obj["type"] == "graph":
                        report_body += self.add_graph(sub_obj["content"], current_run_id, baseline_run_id)
        return report_body