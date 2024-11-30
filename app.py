import os
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from backend.models import db, ServiceCategory, Admin, Professional, User  
from backend.api import *

app=None
def setup_database():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///my_app_db.sqlite3"
    app.config['SECRET_KEY'] = "myappkey"
    db.init_app(app) 
    api.init_app(app)
    login_manager = LoginManager(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        uid = user_id.split("-")
        if uid[0] == 'a':
            return db.session.get(Admin,int(uid[1]))
        elif uid[0] == 'p':
            return db.session.get(Professional,int(uid[1]))
        elif uid[0] == 'u':
            return db.session.get(User,int(uid[1]))
    with app.app_context():
        if not os.path.exists('my_app_db.sqlite3'):
            db.create_all()
            print("Database created.")
        if not ServiceCategory.query.first():
            initial_services = [
                ServiceCategory(
                    name="House Cleaning",
                    base_price=500,
                    tags="House Cleaning,Deep Cleaning,Bathroom Cleaning,Kitchen Cleaning,Pest Control",
                    img_url="/static/category/cleaning.png"
                ),
                ServiceCategory(
                    name="Electrician",
                    base_price=100,
                    tags="Wiring,Lighting Installation,Circuit Breaker Repair,Appliance Installation,Electrical Safety Inspection",
                    img_url="/static/category/Electrician.png"
                ),
                ServiceCategory(
                    name="Carpenter",
                    base_price=750,
                    tags="Furniture Repair,Custom Shelving,Cabinet Installation,Door Fitting,Wood Polishing",
                    img_url="/static/category/carpenter.png"
                ),
                
                ServiceCategory(
                    name="Gardening",
                    base_price=1000,
                    tags="Lawn Mowing,Planting,Weed Control,Garden Maintenance,Soil Preparation",
                    img_url="/static/category/Gardening.png"
                ),
                
            ]
            db.session.bulk_save_objects(initial_services)
            db.session.commit()
            
            
    app.app_context().push()
    app.debug=True
    print("Helpify is started...")


setup_database()

from backend.routes import *


if __name__ == "__main__":
    app.run()
