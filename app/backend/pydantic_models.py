from pydantic import BaseModel


class AzureModel(BaseModel):
    name:              str
    token:             str
    org_url:           str
    project_id:        str
    identifier:        str
    path_to_report:    str
    is_default:        str


class GrafanaModel(BaseModel):
    name:             str
    server:           str
    org_id:           str
    token:            str
    is_default:       str
    dashboards:       list


class InfluxdbModel(BaseModel):
    name:             str
    url:              str
    org_id:           str
    token:            str
    timeout:          str
    bucket:           str
    listener:         str
    is_default:       str


class AtlassianJiraModel(BaseModel):
    name:             str
    email:            str
    token:            str
    org_url:          str
    project_id:       str
    epic_field:       str
    epic_name:        str
    is_default:       str


class AtlassianWikiModel(BaseModel):
    name:             str
    username:         str
    token:            str
    org_url:          str
    parent_id:        str
    space_key:        str
    is_default:       str


class SmtpMailModel(BaseModel):
    name:             str
    server:           str
    port:             int
    use_ssl:          str
    use_tls:          str
    username:         str
    token:            str
    is_default:       str
    recipients:       list


class TemplateObjectModel(BaseModel):
    id:               int
    type:             str
    content:          str


class TemplateModel(BaseModel):
    name:             str
    flow:             str
    title:            str
    data:             list[TemplateObjectModel]


class TemplateGroupModel(BaseModel):
    name:             str
    title:            str
    data:             list[TemplateObjectModel]


class FlowModel(BaseModel):
    name:             str
    influxdb:         str
    grafana:          str
    output:           str


class NfrModel(BaseModel):
    scope:            str
    metric:           str
    aggregation:      str
    operation:        str
    threshold:        int
    weight:           str
    name:             str


class NfrGroupModel(BaseModel):
    name:             str
    rows:             list[NfrModel]