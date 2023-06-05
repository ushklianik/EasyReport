# Flask modules
from flask                   import render_template, request, url_for, redirect, flash, jsonify
from flask_login             import current_user
import traceback

# App modules
from app                     import app
from app.backend.validation.validation import NFR

@app.route('/nfrs', methods=['GET'])
def get_nfrs():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project = request.cookies.get('project')  
        nfr_obj = NFR(project)
        nfrs_list = nfr_obj.get_nfrs()
        return render_template('home/nfrs.html', nfrs_list=nfrs_list)
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for('get_nfrs'))

@app.route('/nfr', methods=['GET', 'POST'])
def get_nfr():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        nfrs = {}
        # Get current project
        project = request.cookies.get('project') 
        if request.method == "POST":
            nfr_obj = NFR(project)
            nfr_obj.save_nfrs(request.get_json())
            flash("NFR saved.")
        elif request.args.get('test_name') != None:
            nfr_obj = NFR(project)
            nfrs = nfr_obj.get_nfr(request.args.get('test_name'))
            return render_template('home/nfr.html', nfrs=nfrs)
    except Exception:
        flash("ERROR: " + str(traceback.format_exc()))
    return jsonify({'redirect_url': 'nfrs'})

@app.route('/delete/nfr', methods=['GET'])
def delete_nfrs():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project = request.cookies.get('project')  
        nfr_obj = NFR(project)
        nfr_obj.delete_nfrs(request.args.get('test_name'))
        flash("NFR deleted.")
        return redirect(url_for('get_nfrs'))
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
        return redirect(url_for('get_nfrs'))