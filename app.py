from flask import Flask, request, render_template, redirect, flash, session
from models import User, db, connect_db, Feedback
from forms import NewUserForm, LoginForm, DeleteForm, FeedbackForm
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import Unauthorized

bcrypt = Bcrypt()

app = Flask(__name__)

app.config['SECRET_KEY'] = "whatever"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///UserDB'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

db.init_app(app)
connect_db(app)

@app.route('/')
def root():    
    return render_template("home.html")
    
@app.route('/register')
def show_registration_form():
    """Route to get and show registration form to create new users."""
    
    form = NewUserForm()
    
    return render_template('users/new_user_form.html', form=form)

@app.route('/register', methods=['POST'])
def submit_new_user():
    """Handle submission of new user form."""
    
    form = NewUserForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        user = User.register(username, password, email, first_name, last_name)
        
        db.session.commit()
        session['username'] = user.username
        
        flash(f"User created.")
        return redirect(f"users/{user.username}")
    else:
        return render_template("users/new_user_form.html", form=form)    

@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    """Route to show login form or handle submission of login information"""
    
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username or password."]
            return render_template("users/user_login_form.html", form=form)
        
    return render_template('users/user_login_form.html', form=form)
        
    

@app.route('/secret')
def secret():    
    return render_template('secret.html')

@app.route("/logout")
def logout():
    """Logout route."""

    session.pop("username")
    return redirect("/login")

@app.route("/users/<username>")
def show_user(username):
    """Example page for logged-in-users."""

    if "username" not in session:
        flash("You must be logged in to view.")
        raise Unauthorized()

    user = User.query.get(username)
    form = DeleteForm()

    return render_template("users/user_show.html", user=user, form=form)

@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    """Delete user and redirect to login page."""
    
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    
    return redirect("/login")

@app.route("/users/<username>/feedback/new", methods=["GET", "POST"])
def new_feedback(username):
    """Show add-feedback form and process it."""

    if "username" not in session or username != session['username']:
        flash("You must be logged in to view content.")
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username,
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("feedback/new.html", form=form)


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update-feedback form and process it."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        flash("You must be logged in to view content.")
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("/feedback/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")

    