# Flask modules
from flask                   import render_template, request, url_for, redirect, flash
from flask_login             import current_user
import traceback

# App modules
from app                     import app
from app.backend.validation.validation import nfr

@app.route('/nfrs', methods=['GET'])
def get_nfrs():
    try:
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Get current project
        project = request.cookies.get('project')  
        nfr_obj = nfr(project)
        nfrs_list = nfr_obj.get_nfrs()
        return render_template('home/nfrs.html', nfrs_list=nfrs_list)
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for('index'))

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
            nfr_obj = nfr(project)
            nfr_obj.save_nfrs(request.get_json())
        if request.args.get('appName') != None:
            nfr_obj = nfr(project)
            nfrs = nfr_obj.get_nfr(request.args.get('appName'))
        return render_template('home/nfr.html', nfrs=nfrs)
    except Exception as er:
        flash("ERROR: " + str(traceback.format_exc()))
    return redirect(url_for('index'))