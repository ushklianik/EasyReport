# Flask modules
from flask import render_template, request, url_for, redirect, flash, jsonify

# App modules
from app                               import app
from app.backend.validation.validation import NFR

import traceback

# Route for getting all non-functional requirements
@app.route('/nfrs', methods=['GET'])
def get_nfrs():
    try:
        # Get current project
        project   = request.cookies.get('project')
        nfr_obj   = NFR(project)
        nfrs_list = nfr_obj.get_nfrs()
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
            nfr_obj = NFR(project)
            nfr_obj.save_nfrs(request.get_json())
            flash("NFR saved.")
            return jsonify({'redirect_url': 'nfrs'})
        elif request.args.get('test_name') is not None:
            nfr_obj = NFR(project)
            nfrs    = nfr_obj.get_nfr(request.args.get('test_name'))
    except Exception:
        flash("ERROR: " + str(traceback.format_exc()))
    return render_template('home/nfr.html', nfrs=nfrs)

# Route for deleting a non-functional requirement
@app.route('/delete/nfr', methods=['GET'])
def delete_nfrs():
    try:
        # Get current project
        project = request.cookies.get('project')
        nfr_obj = NFR(project)
        nfr_obj.delete_nfrs(request.args.get('test_name'))
        flash("NFR deleted.")
        return redirect(url_for('get_nfrs'))
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
        return redirect(url_for('get_nfrs'))