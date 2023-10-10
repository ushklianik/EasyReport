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

from app                    import app
from app.backend            import pkg
from flask                  import render_template, request, url_for, redirect, flash, jsonify


# Route for getting all non-functional requirements
@app.route('/nfrs', methods=['GET'])
def get_nfrs():
    try:
        # Get current project
        project   = request.cookies.get('project')
        nfrs_list = pkg.get_nfrs(project)
        return render_template('home/nfrs.html', nfrs_list=nfrs_list)
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for('get_nfrs'))

# Route for getting a specific non-functional requirement
@app.route('/nfr', methods=['GET', 'POST'])
def get_nfr():
    try:
        nfrs = {}
        # Get current project
        project = request.cookies.get('project')
        if request.method == "POST":
            pkg.save_nfrs(project, request.get_json())
            flash("NFR saved.")
            return jsonify({'redirect_url': 'nfrs'})
        elif request.args.get('test_name') is not None:
            nfrs    = pkg.get_nfr(project, request.args.get('test_name'))
    except Exception:
        flash("ERROR: " + str(traceback.format_exc()))
    return render_template('home/nfr.html', nfrs=nfrs)

# Route for deleting a non-functional requirement
@app.route('/delete/nfr', methods=['GET'])
def delete_nfrs():
    try:
        # Get current project
        project = request.cookies.get('project')
        pkg.delete_nfr(project, request.args.get('test_name'))
        flash("NFR deleted.")
        return redirect(url_for('get_nfrs'))
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
        return redirect(url_for('get_nfrs'))