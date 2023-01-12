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

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    formForMerics = graphForm(request.form)
    # Get current project
    project = request.cookies.get('project')  

    if formForMerics.validate_on_submit():
        viewPanel      = request.form.get("viewPanel")
        dashId         = request.form.get("dashId")
        fileName       = request.form.get("fileName")
        width          = request.form.get("width")
        height         = request.form.get("height")
        msg = pkg.saveGraph(project, viewPanel, dashId, fileName, width, height)

    return render_template('home/all-reports.html')


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