from auth import auth as auth_blueprint
from views import app as app_blueprint
from admin import admin_page as admin_blueprint
from flask_login import LoginManager
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import db
import models
from views import MyView

def create_app():
    app = Flask(__name__,template_folder="templates")
    #setting the admin page
    # app.debug = True
    # app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    # app.config['TEMPLATE_AUTO_RELOAD'] = True

    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3',static_url_path="templates/admin",url='/admin/')
    admin.add_view(MyView(models.User, db.session))
    admin.add_view(MyView(models.Alerts, db.session))
    admin.add_view(MyView(models.Logs, db.session))
    admin.add_view(MyView(models.Rules, db.session))
    admin.add_view(MyView(models.BannedIPAddress, db.session))
    admin.add_view(MyView(models.BannedCountries, db.session))
    admin.add_view(MyView(models.BannedBrowsers, db.session))
    admin.add_view(MyView(models.AllowedTime, db.session))
    admin.add_view(MyView(models.AllowedTries, db.session))
    admin.add_view(MyView(models.Counter, db.session))
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql6679615:nmZ7pdVmPA@sql6.freesqldatabase.com/sql6679615'
    db.init_app(app)
    #db = SQLAlchemy(app)
    return app



app = create_app()
@app.before_request
def create_tables():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'auth.login' # type: ignore
login_manager.init_app(app)

# app.add_url_rule('/admin/','admin',adf)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return models.User.query.get(int(user_id))


app.register_blueprint(auth_blueprint)
app.register_blueprint(app_blueprint)
app.register_blueprint(admin_blueprint)

app.run("127.0.0.1",8000)

