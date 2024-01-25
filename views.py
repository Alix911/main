from flask import Blueprint,render_template,redirect,url_for,abort
from flask_admin.contrib.sqla import ModelView
from flask_login import login_required, logout_user, current_user
from models import Alerts, Rules,Logs,User,AllowedTime,db
from datetime import datetime

app = Blueprint('app', __name__)



class MyView(ModelView):
    
    def is_accessible(self):
        if current_user.is_authenticated:
            if not current_user.is_admin:
                abort(403,"YOU ARE NOT AUTHORIZED TO VIEW THIS PAGE")
            else:
                return current_user.is_authenticated
        else:
            return not current_user.is_authenticated
        
    def inaccessible_callback(self, name, **kwargs):
        return "<h1>YOU ARE NOT AUTHORIZED TO VIEW THIS PAGE</h1>"

def is_admin():

    if current_user.is_admin == True:
        return True
    else:
        return redirect(url_for("admin_page.admin_login"))
# def not_admin():

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@app.route('/')
@login_required
def home():

    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.index"))
        else:
            return render_template("Welcome.html")
            
    else:
        return redirect(url_for("admin_page.admin_login"))
    



# @app.route('/home')
# @login_required
# def root():
#     if is_admin() != True:
#         abort(404,"Page not found")
#     else:
#         return redirect(url_for('admin.index'))

@app.route('/admin/')
@login_required
def admin():
    if is_admin() != True:
        abort(404,"Page not found")
    else:
        return redirect(url_for('admin_page.admin_login'))

@app.route('/admin/dashboard', methods=["GET"])
@login_required
def dashboard():
    is_admin()
    alerts = Alerts.query.filter().all()
    logs = Logs.query.filter().all()

    # fetching the blocks and the time they were happened
    times = [(user.user_id,user.time) for user in alerts if not user.message.endswith("has created a session successfully")]
    weekly = 0
    monthly = 0
    print(len(alerts),len(times))    
    for t in times:
        # print(t[1].day)
        if t[1].day in range(datetime.now().date().day-7,datetime.now().date().day+1):
            weekly+=1
        if t[1].month == datetime.now().date().month:
            monthly+=1
    alert = [{"time":alert.time,"message":Alerts.query.filter_by(user_id=alert.user_id).first().message} for alert in alerts][-4:]
    log = [{"id":log.user_id,"user":User.query.filter_by(id=log.user_id).first().name,"priority":log.priority,"blocks":User.query.filter_by(id=log.user_id).first().blocks,"color":log.color} for log in logs]
    context = {"alert":alert,"log":log,"weekly":weekly,"monthly":monthly}

    return render_template("admin/dashboard.html",context=context)
    
@app.route('/admin/alerts', methods=["GET"])
@login_required
def alerts():
    is_admin()
    alerts = Alerts.query.filter().all()
    
    context = [{"time":alert.time,"message":Alerts.query.filter_by(user_id=alert.user_id).first().message} for alert in alerts]
    return render_template("admin/alerts.html",context=context)
    
@app.route('/admin/log', methods=["GET"])
@login_required
def logs():
    is_admin()
    logs = Logs.query.filter().all()
    context = [{"id":log.user_id,"user":User.query.filter_by(id=log.user_id).first().name,"priority":log.priority,"blocks":User.query.filter_by(id=log.user_id).first().blocks,"color":log.color} for log in logs]
    return render_template("admin/logs.html",context=context)
    

@app.route('/admin/rules', methods=["GET"])
@login_required
def rules():
    is_admin()
    rules = Rules.query.filter().all()
    context = [{"id":rule.rule_id,"text":rule.rule} for rule in rules]
    return render_template("admin/rules.html",context=context)
    

