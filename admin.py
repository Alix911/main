from flask import Blueprint, render_template, redirect, url_for,request,flash
from flask_login import login_user,logout_user,login_required
from werkzeug.security import check_password_hash
from models import db, User

admin_page = Blueprint('admin_page', __name__)

@admin_page.route('/admin/login')
def admin_login():
    # if the database is courrupted or deleted uncomment this block to add the admin user to the new 
    # database 
        
        # admin = User(id=0,name="Admin",email="admin@admin.com",password="admin",blocks=0,is_admin=True)
        # db.session.add(admin)
        # db.session.commit()

    # if you forgot the admin password uncomment this block to set it as "admin"
        
        # db.session.query(User).filter().all()[0].password = "scrypt:32768:8:1$sDTfv0H7f9tvF2ke$5afca684a15c48aed449c121b7facb1538211cfd9ddc723a1950b363335b6dcc02ebea1946fdb9ee8b18055ea215331afe4176dc4903de1baf50c244fe1159bd"
        # db.session.commit()
    
    return render_template("admin-login.html")

@admin_page.route('/admin/login', methods=["POST"])
def admin_login_post():
    email = request.form.get('email')
    password = request.form.get('pass')

    user = db.session.query(User).filter_by(email=email).first()
    if check_password_hash(user.password, password) == False:
        flash("Invalid Credentials")
        return redirect(url_for("admin_page.admin_login"))
    else:
        if user.is_admin == True: 
            login_user(user)
            return redirect(url_for('admin.index'))

        else:
            flash("User is not registered as admin")
            return redirect(url_for('auth.login'))


@admin_page.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))