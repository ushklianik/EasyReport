# Flask modules
from flask                   import render_template, request, url_for, redirect, flash
from flask_login             import current_user
import traceback

# App modules
from app                     import app
from app.forms               import GraphForm
from app.backend             import pkg


@app.route('/graphs', methods=['GET'])
def get_graphs():
    try:
        # Get current project
        project = request.cookies.get('project')  
        # Declare the graphs form
        form_for_graphs = GraphForm(request.form)
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
        graph_name = request.args.get('graph_name')
        if graph_name != None:
            pkg.delete_graph(project, graph_name)
            flash("Graph deleted")
    except Exception as er:
        flash("ERROR: " + str(er))
    return redirect(url_for('get_graphs'))