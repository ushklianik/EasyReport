import time

from app.backend.reporting.reporting_base    import ReportingBase
from app.backend.integrations.main.smtp_mail import SmtpMail
from datetime                                import datetime


class SmtpMailReport(ReportingBase):

    def __init__(self, project):
        super().__init__(project)
        self.report_body = ""
        self.images      = []

    def set_template(self, template):
        super().set_template(template)
        self.output_obj = SmtpMail(project=self.project, name=self.output)

    def add_group_text(self, text):
        text = f'<p>{text}</p><br>'
        text = text.replace('\n', '<br>')
        return text

    def add_text(self, text):
        text = self.replace_variables(text)
        text = f'<p>{text}</p>'
        text = text.replace('\n', '<br>')
        return text
    
    def add_graph(self, name, current_run_id, baseline_run_id):
        image = self.grafana_obj.render_image(name, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        if(image):
            timestamp  = str(round(time.time() * 1000))
            content_id = f"{self.test_name}_{name}_{timestamp}"
            content_id = content_id.replace(' ', '_')
            file_name  = f"{content_id}.png"
            self.images.append({'file_name':file_name, 'data': image, 'content_id': content_id})
            graph      = f'<img src="cid:{content_id}" width="900" alt="{content_id}" /><br>'
        else:
            graph      = f'Image failed to load, name: {name}'
        return graph

    def generate_path(self, isgroup):
        if isgroup: 
            title = self.group_title
        else:
            title = self.replace_variables(self.title)
        return title

    def generate_report(self, tests, template_group=None):
        templates_title = ""
        group_title     = None
        def process_test(test):
            nonlocal templates_title
            template_id = test.get('template_id')
            if template_id:
                self.set_template(template_id)
                run_id            = test.get('runId')
                baseline_run_id   = test.get('baseline_run_id')
                title             = self.generate_path(False)
                self.report_body += f'<h3>{title}</h3>'
                self.report_body += self.generate(run_id, baseline_run_id)
                if not group_title:
                    templates_title += f'{title} | '
        if template_group:
            self.set_template_group(template_group)
            group_title       = self.generate_path(True)
            self.report_body += f'<h2>{group_title}</h2>'
            for obj in self.template_order:
                if obj["type"] == "text":
                    self.report_body += self.add_group_text(obj["content"])
                elif obj["type"] == "template":
                    for test in tests:
                        if obj.get('content') == test.get('template_id'):
                            process_test(test)
        else:
            for test in tests:
                process_test(test)
        current_time = datetime.now()
        time_str     = current_time.strftime("%d.%m.%Y %H:%M")
        if not group_title:
            templates_title += time_str
            self.output_obj.put_page_to_mail(templates_title, self.report_body, self.images)
        else:
            group_title += f' {time_str}'
            self.output_obj.put_page_to_mail(group_title, self.report_body, self.images)
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