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
    token_type:       str
    org_url:          str
    project_id:       str
    epic_field:       str
    epic_name:        str
    is_default:       str


class AtlassianConfluenceModel(BaseModel):
    name:                  str
    email:                 str
    token:                 str
    token_type:            str
    org_url:               str
    space_key:             str
    parent_id:             str
    is_default:            str


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