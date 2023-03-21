import os

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User
from forms import RegisterUserForm, LoginUserForm, LogoutForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///notes')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)  # debug


@app.get("/")
def redirect_to_register():
    """Redirects to register"""

    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    """Registers a user if form is submitted. Otherwise shows register form."""

    form = RegisterUserForm()

    if form.validate_on_submit():

        user = User.register_user(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )

        db.session.add(user)
        db.session.commit()

        session['username'] = user.username

        return redirect(f'/users/{user.username}')
    else:
        return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Logs in a user if form is submitted. Redirects to user page if
        user is already logged in. Otherwise renders login form"""

    if session.get("username"):
        return redirect (f"/users/{session['username']}")

    form = LoginUserForm()

    if form.validate_on_submit():

        user = User.authenticate_user(
            username=form.username.data,
            password=form.password.data
        )

        if user: 
            session['username'] = user.username

            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ["Bad username/password"]

    return render_template('login.html', form=form)


@app.get('/users/<username>')
def show_user_details(username):
    """ shows user info. If accessing wrong user, redirect to login """

    if username == session.get('username'):

        user = User.query.get(username)

        return render_template('user.html', user=user)
    else:
        flash("Cannot access this user")
        return redirect('/login')
    
@app.post('/logout')
def logout_user():
    """logs out the current user"""

    form = LogoutForm()

    if form.validate_on_submit():
        session.pop("username", None)

    return redirect("/")