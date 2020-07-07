from flask import Flask, redirect, render_template, session
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from werkzeug.exceptions import Unauthorized
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///desserts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "cool123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.route("/")
def home_page():
    """Redirect to register"""

    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def create_account():
    """Show form to create account"""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User(
            username=username, 
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)
        db.session.commit()

        return redirect(f"/users/{user.username}")
    
    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Generate login form and handle login"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Invalid name/password"]
            return render_template("login.html", form=form)
    
    return render_template("login.html", form=form)

    @app.route("/logout")
    def logout():
        """Log out of session"""

        session.pop("username")
        return redirect("/")

    @app.route("/users/<username>")
    def show_user(username):
        """Show user information"""

        if "username" not in session or username != session['username']:
            raise Unauthorized()

        user = User.query.get(username)
        form = DeleteForm()

        return render_template("show_user.html", user=user, form=form) 

    @app.route("/users/<username>/add", methods=["GET", "POST"])
    def add_new_feedback(username):
        """Add new user feedback"""

        if "username" not in session or username != session['username']:
            raise Unauthorized()
        
        form = FeedbackForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            feedback = Feedback(
                title=title,
                content=content,
                username=username
            )

            db.session.add(feedback)
            db.session.commit()

            return redirect(f"/users/{feedback.username}")
        
        else: 
            render_template("new_feedback_form.html", form=form)

    @app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
    def update_feedback(feedback_id):
        """Update feedback"""

        if "username" not in session or username != session['username']:
            raise Unauthorized()

        feedback = Feedback.query.get(feedback_id)

        form = FeedbackForm(obj=feedback)

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.DeprecationWarning

            db.session.commit()

            return redirect(f"/users/{feedback.username}")
        
        else:
            return render_template("edit_feedback_form.html", form=form)

    @app.route("/feedback/<int:feedback_id/delete", methods=["POST"])
    def delete_feedback(feedback_id):
        """Delete feedback"""

        if "username" not in session or username != session['username']:
            raise Unauthorized()

        form = DeleteForm()

        if form.validate_on_submit():
            db.session.delete(feedback)
            db.session.commit()

        return redirect(f"/users/{feedback.username}", form=form)

    @app.route("/users/<username>/delete", methods=["POST"])
    def delete_user(username):
        """Delete user"""

        if "username" not in session or username != session['username']:
            raise Unauthorized()

        user = User.query.get(username)
        db.session.delete(user)
        db.session.commit()
        session.pop("username")

        return redirect("/")