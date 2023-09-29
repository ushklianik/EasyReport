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