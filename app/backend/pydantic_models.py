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
    name:             str
    server:           str
    org_id:           str
    token:            str
    is_default:       str
    dashboards:       list

class influxdb_model(BaseModel):
    name:             str
    url:              str
    org_id:           str
    token:            str
    timeout:          str
    bucket:           str
    listener:         str
    is_default:       str

class atlassian_jira_model(BaseModel):
    name:             str
    email:            str
    token:            str
    org_url:          str
    project_id:       str
    epic_field:       str
    epic_name:        str
    is_default:       str

class atlassian_wiki_model(BaseModel):
    name:             str
    username:         str
    token:            str
    org_url:          str
    parent_id:        str
    space_key:        str
    is_default:       str

class template_object_model(BaseModel):
    id:               int
    type:             str
    content:          str
    
class template_model(BaseModel):
    name:             str
    flow:             str
    title:            str
    data:             list[template_object_model]

class flow_model(BaseModel):
    name:             str
    influxdb:         str
    grafana:          str
    output:           str

class nfr(BaseModel):
    scope:            str
    metric:           str
    aggregation:      str
    operation:        str  
    threshold:        int      
    weight:           str
    name:             str

class nfr_group(BaseModel):
    name:             str
    rows:             list[nfr]