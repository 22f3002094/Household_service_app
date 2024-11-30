import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=True)
    
    def get_id(self):
        return f'a-{self.id}'


class Professional(db.Model, UserMixin):
    __tablename__ = 'professional'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    address = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    experience = db.Column(db.Integer)
    phone = db.Column(db.String)
    city = db.Column(db.String)
    status = db.Column(db.String)
    resume=db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    all_plans = db.relationship("ServicePlan", backref="professional", cascade="all, delete-orphan")
    assigned_booking = db.relationship("Booking", backref="professional", cascade="all, delete-orphan")
    def get_id(self):
        return f'p-{self.id}'

class User(db.Model, UserMixin):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    address = db.Column(db.String)
    city = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    phone = db.Column(db.String)
    status=db.Column(db.String)
    sent_booking = db.relationship("Booking", backref="customer")
    def get_id(self):
        return f'u-{self.id}'


class ServiceCategory(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    base_price = db.Column(db.Integer)
    tags = db.Column(db.String)
    img_url = db.Column(db.String, unique=True)
    service_plans = db.relationship("ServicePlan", backref="category")
    professionals = db.relationship("Professional", backref="category",cascade="all, delete-orphan")


class ServicePlan(db.Model):
    __tablename__ = "service_plan"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    price = db.Column(db.Integer)
    description = db.Column(db.String)
    planimg=db.Column(db.String)
    tags=db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("professional.id"), nullable=False)
    bookings = db.relationship("Booking", backref="service_plan")

class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.String)
    time = db.Column(db.String)
    address = db.Column(db.String)
    status = db.Column(db.String)
    rating = db.Column(db.Integer)
    ratingmessage=db.Column(db.String)
    remark=db.Column(db.String)
    professional_id = db.Column(db.Integer, db.ForeignKey("professional.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    service_plan_id = db.Column(db.Integer, db.ForeignKey("service_plan.id"), nullable=False)



