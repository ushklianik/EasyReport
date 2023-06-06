# Python modules
from app.backend import pkg

# Flask modules
from flask import flash, redirect, request, url_for

# App modules
from app import app

# Route for setting the current project
@app.route('/set-project', methods=['GET'])
def setProject():
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
def getProjects():
    try:
        # Get all projects
        projects = pkg.get_projects()
    except Exception as er:
        flash("ERROR: " + str(er))
    return {'projects': projects}