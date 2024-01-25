import datetime
from types import NoneType
from flask import Blueprint, render_template, redirect, url_for,request,flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,logout_user,login_required
from models import Alerts, db, User
from core import checks


auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/login', methods=["POST"])
def login_post():
    email = request.form.get('email')
    password = request.form.get('pass')
    remember = True if request.form.get('remember') else False
    ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
    print("Client's IP Address:", ip)
    user_agent = request.user_agent
    user = db.session.query(User).filter_by(email=email).first()
    
    if user is None:
        flash("User does not exists !")
        return redirect(url_for('auth.login'))


    elif user.is_admin == True:
        return redirect(url_for('admin_page.admin_login'))
    
    
    else:
        # Verify password for non-admin user
        if not check_password_hash(user.password, password):
            flash("Invalid password.")
            return redirect(url_for("auth.login"))
        
        check = checks.Checks(user,password,ip,user_agent)
        check_result = check.checkTries()
        print(check_result)
        if check_result == True:
            check.checkIP()
            check.checkCountry()
            check.check_time()
            check.checkBrowser()
            alert = Alerts(user_id=user.id, message=f"{user.name} has created a session successfully", time=datetime.datetime.now())
            db.session.add(alert)
            db.session.commit()
            login_user(user, remember)
            return redirect(url_for('app.home'))
    
        elif check_result == "Invalid Password":
            flash("Invalid Password")
            return redirect(url_for("auth.login"))
        
        else:
            # Handle unexpected return value
            flash("An unexpected error occurred.")
            return redirect(url_for("auth.login"))


@auth.route('/register')
def register():
    return render_template("register.html")

@auth.route('/register', methods=['POST'])
def register_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('pass')
    
    user = db.session.query(User).filter_by(email=email).first() # if this returns a user, then the email already exists in database
    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.register'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, password=generate_password_hash(password, method='scrypt'),name=name)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('app.home'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

