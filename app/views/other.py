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

from app         import app
from app.backend import pkg
from flask       import flash, redirect, request, url_for


# Route for setting the current project
@app.route('/set-project', methods=['GET'])
def set_project():
    try:
        # Get current project
        project = request.args.get('project')
        # If project not provided, the default value is selected
        if project is None:
            project = "default"
        res = redirect(url_for('index'))
        res.set_cookie(key='project', value=project, max_age=None)
    except Exception as er:
        flash("ERROR: " + str(er))
    return res

# Route for getting all available projects
@app.route('/get-projects', methods=['GET'])
def get_projects():
    try:
        # Get all projects
        projects = pkg.get_projects()
    except Exception as er:
        flash("ERROR: " + str(er))
    return {'projects': projects}

@app.route('/save-project', methods=['GET'])
def save_project():
    try:
        project = request.args.get('project_name')
        pkg.save_project(project) 
    except Exception as er:
        flash("ERROR: " + str(er))
        return str(er)
    return "Saved."

@app.route('/delete-project', methods=['GET'])
def delete_project():
    try:
        project = request.args.get('project')
        pkg.delete_project(project) 
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for("index"))