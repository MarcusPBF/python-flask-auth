from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# Create login manager
login_manager = LoginManager()
login_manager.init_app(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
 
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("secrets"))

    if request.method == 'POST':
        user = db.session.execute(db.select(User).where(User.email == request.form['email'])).scalar()

        if user is not None:
            flash("Email already exists in the database. Please use another email.")
            return redirect(url_for('register'))

        new_user = User(
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            name=request.form['name'],
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("secrets"))

    return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("secrets"))

    if request.method == 'POST':
        user = db.session.execute(db.select(User).where(User.email == request.form['email'])).scalar()

        if user is None or not check_password_hash(user.password, request.form['password']):
            flash("Invalid Username and/or password. Please try again.")
            return redirect(url_for('login'))

        if check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for("secrets"))

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/download')
@login_required
def download():
    return send_from_directory("static",path="files/cheat_sheet.pdf")

if __name__ == "__main__":
    app.run(debug=True)
