# Python modules
from app.backend import pkg

# Flask modules
from flask                   import render_template, request, url_for, redirect
from flask_login             import current_user

# App modules
from app         import app
from app.forms   import graphForm

@app.route('/new-graph', methods=['POST'])
def newGraph():
    msg = None

    project = request.cookies.get('project') 
    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == "POST":
        msg = pkg.saveGraph(project, request.get_json())
        print(request.get_json())
    return msg


@app.route('/set-project', methods=['GET'])
def setProject():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.args.get('project')
    # If project not provided, the default value is selected
    if project == None:
        project = "default"

    res = redirect(url_for('index'))
    res.set_cookie(key = 'project', value = project, max_age=None)
    return res

@app.route('/get-projects', methods=['GET'])
def getProjects():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get all projects
    projects = pkg.getProjects()
    return {'projects': projects}