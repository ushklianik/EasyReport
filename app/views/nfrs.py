# Flask modules
from flask                   import render_template, request, url_for, redirect
from flask_login             import current_user

# App modules
from app                     import app
from app.backend.validation.validation import nfr

@app.route('/nfrs', methods=['GET'])
def getNFRs():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get current project
    project = request.cookies.get('project')  
    nfrObject = nfr(project)
    nfrsList = nfrObject.getNFRs()

    return render_template('home/nfrs.html', nfrsList=nfrsList)

@app.route('/nfr', methods=['GET', 'POST'])
def getNFR():

    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
        
    nfrs = {}
    # Get current project
    project = request.cookies.get('project') 

    if request.method == "POST":
        nfrObject = nfr(project)
        nfrObject.saveNFRs(request.get_json())
    
    if request.args.get('appName') != None:
        nfrObject = nfr(project)
        nfrs = nfrObject.getNFR(request.args.get('appName'))

    return render_template('home/nfr.html', nfrs=nfrs)