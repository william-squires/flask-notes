import os

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User, Note
from forms import RegisterUserForm, LoginUserForm, CSRFForm, NoteForm

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

    if session.get("username"):
        flash("Cannot register while logged in")
        return redirect(f"/users/{session['username']}")

    form = RegisterUserForm()

    if form.validate_on_submit():

        user = User.register(
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
        return redirect(f"/users/{session['username']}")

    form = LoginUserForm()

    if form.validate_on_submit():

        user = User.authenticate(
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

    form = CSRFForm()

    if username == session.get('username'):

        user = User.query.get(username)

        return render_template('user.html', user=user, form=form)
    else:
        flash("Cannot access this user")
        return redirect('/login')


@app.post('/logout')
def logout_user():
    """logs out the current user"""

    form = CSRFForm()

    if form.validate_on_submit():
        session.pop("username", None)

    return redirect("/")


@app.post('/users/<username>/delete')
def delete_user(username):
    """ delete user from database with all their notes,
    then redirects to home """

    redirect_if_not_logged_in(username)
    form = CSRFForm()

    if form.validate_on_submit():
        session.pop("username", None)

        user = User.query.get(username)
        notes = user.notes

        for note in notes:
            db.session.delete(note)
        db.session.delete(user)
        db.session.commit()

        return redirect('/')
    else:
        flash('Must be logged in.')

        return redirect('/')


@app.route('/users/<username>/notes/add', methods=['GET', 'POST'])
def add_note(username):
    """ add note and redirect to user page. """

    form = NoteForm()

    redirect_if_not_logged_in(username)

    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            owner=username
        )

        db.session.add(note)
        db.session.commit()

        return redirect(f'/users/{username}')
    else:
        return render_template('create_note.html', form=form)


@app.route('/notes/<int:note_id>/update', methods=['GET', 'POST'])
def update_note(note_id):
    """ update note and redirect to user page. """

    note = Note.query.get_or_404(note_id)
    username = note.user.username

    redirect_if_not_logged_in(username)

    form = NoteForm()

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{note.user.username}')
    else:

        form.title.data = note.title
        form.content.data = note.content
        return render_template('update_note.html', form=form)


@app.post('/notes/<int:note_id>/delete')
def delete_note(note_id):
    """ delete a user's note"""

    note = Note.query.get_or_404(note_id)
    username = note.user.username

    redirect_if_not_logged_in(username)

    form = CSRFForm()

    if form.validate_on_submit():

        db.session.delete(note)
        db.session.commit()

        return redirect(f'/users/{username}')
    else:
        flash('Must be logged in.')

        return redirect('/')


def redirect_if_not_logged_in(username):
    if username != session['username']:
        flash('You must be logged in.')
        return redirect('/')