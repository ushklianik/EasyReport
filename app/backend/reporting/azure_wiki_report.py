from app.backend.integrations.main.azure_wiki import AzureWiki
from app.backend.reporting.reporting_base     import ReportingBase


class AzureWikiReport(ReportingBase):

    def __init__(self, project):
        super().__init__(project)
        self.report_body = ""

    def set_template(self, template):
        super().set_template(template)
        self.output_obj = AzureWiki(project=self.project, name=self.output)

    def add_group_text(self, text):
        text += f'\n\n'
        return text

    def add_text(self, text):
        text = self.replace_variables(text)
        text += f'\n\n'
        return text

    def add_graph(self, name, current_run_id, baseline_run_id):
        image    = self.grafana_obj.render_image_encoded(name, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        fileName = self.output_obj.put_image_to_azure(image, name)
        graph    = f'![image.png](/.attachments/{str(fileName)})\n\n'
        return graph

    def generate_path(self, isgroup):
        if isgroup:
            title = f'{self.output_obj.get_path()}{self.group_title}'
        else:
            title = f'{self.output_obj.get_path()}{self.replace_variables(self.title)}'
        return title

    def generate_report(self, tests, template_group=None):
        path = None
        def process_test(test, isgroup):
            nonlocal path
            template_id = test.get('template_id')
            if template_id:
                self.set_template(template_id)
                run_id            = test.get('runId')
                baseline_run_id   = test.get('baseline_run_id')
                self.report_body += self.generate(run_id, baseline_run_id)
                if not path:
                    path = self.generate_path(isgroup)
        if template_group:
            self.set_template_group(template_group)
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
        self.output_obj.create_or_update_page(path, self.report_body)
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