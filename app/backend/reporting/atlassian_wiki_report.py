from app.backend.reporting.reporting_base         import ReportingBase
from app.backend.integrations.main.atlassian_wiki import AtlassianWiki
from datetime                                     import datetime


class AtlassianWikiReport(ReportingBase):

    def __init__(self, project):
        super().__init__(project)
        self.report_body = ""
        self.page_id     = None

    def set_template(self, template):
        super().set_template(template)
        self.output_obj = AtlassianWiki(project=self.project, name=self.output)

    def add_group_text(self, text):
        text += f'\n\n'
        text = text.replace('\\"', '"')
        text = text.replace('&', '&amp;')
        return text

    def add_text(self, text):
        text = self.replace_variables(text)
        text += f'\n\n'
        text = text.replace('\\"', '"')
        text = text.replace('&', '&amp;')
        return text
    
    def add_graph(self, name, current_run_id, baseline_run_id):
        image = self.grafana_obj.render_image(name, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        fileName = self.output_obj.put_image_to_confl(image, name, self.page_id, current_run_id)
        if(fileName):
            graph = f'<ac:image ac:align="center" ac:layout="center" ac:original-height="500" ac:original-width="1000"><ri:attachment ri:filename="{str(fileName)}" /></ac:image>\n\n'
        else:
            graph = f'Image failed to load, name: {name}'
        return graph

    def generate_path(self, isgroup):
        if isgroup:
            title = self.group_title
        else:
            title = self.replace_variables(self.title)
        return title

    def create_page_id(self, page_title):
        response     = self.output_obj.put_page(title=page_title, content="")
        self.page_id = response["id"]

    def generate_report(self, tests, template_group=None):
        templates_title = ""
        group_title     = None
        def process_test(test, isgroup):
            nonlocal templates_title
            nonlocal group_title
            template_id = test.get('template_id')
            if template_id:
                self.set_template(template_id)
                run_id          = test.get('runId')
                baseline_run_id = test.get('baseline_run_id')
                if not self.page_id:
                    if isgroup:
                        group_title = self.generate_path(True)
                        self.create_page_id(group_title)
                    else:
                        temporary_title = self.generate_path(False)
                        self.create_page_id(temporary_title)
                title             = self.generate_path(False)
                self.report_body += self.add_text(title)
                self.report_body += self.generate(run_id, baseline_run_id)
                if not group_title:
                    templates_title += f'{title} | '
        if template_group:
            self.set_template_group(template_group)
            title             = self.generate_path(True)
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
        time_str     = current_time.strftime("%d.%m.%Y %H:%M")
        if not group_title:
            templates_title += time_str
            self.output_obj.update_page(page_id=self.page_id, title=templates_title, content=self.report_body)
        else:
            group_title += f' {time_str}'
            self.output_obj.update_page(page_id=self.page_id, title=group_title, content=self.report_body)
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