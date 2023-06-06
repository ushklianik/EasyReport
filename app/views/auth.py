# Flask modules
from flask       import render_template, request, url_for, redirect, flash
from flask_login import login_user, logout_user
from jinja2      import TemplateNotFound

# App modules
from app        import app, lm, db, bc
from app.models import Users
from app.forms  import LoginForm, RegisterForm


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Logout user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        # declare the Registration Form
        form = RegisterForm(request.form)
        msg     = None
        success = False
        if request.method == 'GET': 
            return render_template( 'accounts/register.html', form=form, msg=msg )
        # check if both http method is POST and form is valid on submit
        if form.validate_on_submit():
            # assign form data to variables
            username = request.form.get('username', '', type=str)
            password = request.form.get('password', '', type=str) 
            email    = request.form.get('email'   , '', type=str) 
            # filter User out of database through username
            user = Users.query.filter_by(user=username).first()
            # filter User out of database through username
            user_by_email = Users.query.filter_by(email=email).first()
            if user or user_by_email:
                msg = 'Error: User exists!'
            else:         
                pw_hash = bc.generate_password_hash(password)
                user = Users(username, email, pw_hash)
                user.save()
                msg     = 'User created, please <a href="' + url_for('login') + '">login</a>'     
                success = True
        else:
            msg = 'Input error'     
        return render_template( 'accounts/register.html', form=form, msg=msg, success=success )
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('register'))

# Authenticate user
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # Declare the login form
        form = LoginForm(request.form)
        # Flask message injected into the page, in case of any errors
        msg = None
        # check if both http method is POST and form is valid on submit
        if form.validate_on_submit():
            # assign form data to variables
            username = request.form.get('username', '', type=str)
            password = request.form.get('password', '', type=str) 
            # filter User out of database through username
            user = Users.query.filter_by(user=username).first()
            if user:   
                if bc.check_password_hash(user.password, password):
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    msg = "Wrong password. Please try again."
            else:
                msg = "Unknown user"
        return render_template( 'accounts/login.html', form=form, msg=msg )
    except Exception as er:
        flash("ERROR: " + str(er))
        return redirect(url_for('login'))

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):
    try:    
        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( 'home/' + path)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except:
        return render_template('home/page-500.html'), 500