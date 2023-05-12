from pydantic import BaseModel

class azure_model(BaseModel):
    name:              str
    token:             str
    org_url:           str
    project_id:        str
    identifier:        str
    path_to_report:    str
    is_default:        str

class grafana_model(BaseModel):
    name:                  str
    server:                str
    org_id:                str
    token:                 str
    dashboard_id:          str
    dash_render_path:      str
    dash_render_comp_path: str

class influxdb_model(BaseModel):
    name:             str
    url:              str
    org_id:           str
    token:            str
    timeout:          str
    bucket:           str
    measurement:      str
    is_default:       str

class atlassian_jira_model(BaseModel):
    name:                str
    email:               str
    token:               str
    org_url:             str
    project_id:          str
    epic:                str
    is_default:          str
    

class atlassian_wiki_model(BaseModel):
    name:             str
    username:         str
    token:            str
    org_url:          str
    parent_id:        str
    space_key:        str
    is_default:       str
