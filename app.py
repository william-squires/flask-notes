import os
#TODO: clean up imports as needed
from flask import Flask, request, jsonify, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User
from forms import RegisterUserForm, LoginUserForm

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
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

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

        session['username'] = form.username.data

        db.session.add(user)
        db.session.commit()

        return redirect(f'/users/{form.username.data}')
    else:
        return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Logs in a user if form is submitted. Otherwise shows login form."""

    form = LoginUserForm()

    if form.validate_on_submit():

        user = User.authenticate_user(
            username=form.username.data,
            password=form.password.data
        )

        if user:
            session['username'] = form.username.data

            return redirect(f'/users/{form.username.data}')

    return render_template('login.html', form=form)


@app.get('/users/<username>')
def show_user_details(username):
    """ shows user info """

    if username == session.get('username'):

        user = User.query.get(username)

        return render_template('user.html', user=user)
    else:
        return redirect('/login')