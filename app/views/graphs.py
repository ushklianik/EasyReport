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

import traceback

from app         import app
from app.backend import pkg
from app.forms   import GraphForm
from flask       import render_template, request, url_for, redirect, flash


# Route for getting all graphs
@app.route('/graphs', methods=['GET'])
def get_graphs():
    try:
        # Get current project
        project                         = request.cookies.get('project')
        # Declare the graphs form
        form_for_graphs                 = GraphForm(request.form)
        graphs_list                     = pkg.get_graphs(project)
        form_for_graphs.dash_id.choices = pkg.get_dashboards(project)
        return render_template('home/graphs.html', graphs_list=graphs_list, form_for_graphs=form_for_graphs)
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for('index'))

# Route for saving a graph
@app.route('/save-graph', methods=['POST'])
def save_graph():
    try:
        project = request.cookies.get('project')
        if request.method == "POST":
            pkg.save_graph(project, request.form.to_dict())
        flash("Graph updated")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('get_graphs'))

# Route for deleting a graph
@app.route('/delete-graph', methods=['GET'])
def delete_graph():
    try:
        project    = request.cookies.get('project')
        graph_name = request.args.get('graph_name')
        if graph_name is not None:
            pkg.delete_graph(project, graph_name)
            flash("Graph deleted")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('get_graphs'))