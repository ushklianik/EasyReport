# Flask modules
from flask                   import render_template, request, url_for, redirect, flash
from flask_login             import current_user
import traceback

# App modules
from app                     import app
from app.forms               import graph_form
from app.backend             import pkg


@app.route('/graphs', methods=['GET'])
def get_graphs():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project = request.cookies.get('project')  
        # Declare the graphs form
        form_for_graphs = graph_form(request.form)
        graphs_list = pkg.get_graphs(project)
        form_for_graphs.dash_id.choices  = pkg.get_dashboards(project)
        return render_template('home/graphs.html', graphs_list=graphs_list, form_for_graphs=form_for_graphs)
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for('index'))
    
@app.route('/save-graph', methods=['POST'])
def save_graph():
    try:
        project = request.cookies.get('project') 
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if request.method == "POST":
            pkg.save_graph(project, request.form.to_dict())
        flash("Graph updated")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('get_graphs'))

@app.route('/delete-graph', methods=['GET'])
def delete_graph():
    try:
        project = request.cookies.get('project') 
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        graph_name = request.args.get('graph_name')
        if graph_name != None:
            pkg.delete_graph(project, graph_name)
            flash("Graph deleted")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('get_graphs'))