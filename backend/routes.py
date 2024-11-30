#App routes
from flask import Flask,render_template,request,url_for,redirect,flash
from .models import *
from flask import current_app as app
from datetime import datetime
from sqlalchemy import func,or_
from werkzeug.utils import secure_filename
import os
import requests
from PyPDF2 import PdfReader, PdfWriter
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib
matplotlib.use('agg')

from flask_login import LoginManager, login_user, logout_user, login_required, current_user,UserMixin

@app.route("/",methods=["GET","POST"])
def start():
    return render_template("/start.html")



@app.route("/register/<user_type>",methods=["GET","POST"])
def register(user_type):
    if user_type=="customer" and request.method == "GET":
        flash("Welcome register as customer","success")
        return render_template("/Customer/register.html")
    
    elif user_type=="customer" and request.method=="POST":
        cname = request.form.get("c_name")
        cemail = request.form.get("c_email")
        cphone = request.form.get("c_phone")
        ccity = request.form.get("c_city")
        cpassword = request.form.get("c_password")
        caddress = request.form.get("c_address")
        cust = User.query.filter_by(email=cemail).first()
        if cust:
            flash("Email Id already exist!! user different Email Insted")
            return redirect("/register/customer")
        else:
            newcust=User(name=cname,email=cemail,phone=cphone,city=ccity,password=cpassword,address=caddress,status="Active")
            db.session.add(newcust)
            db.session.commit()
            flash("Your profile has been created please login and enjoy our Services.")
            return redirect("/login")

    elif user_type=="professional" and request.method =="GET":
        categories=ServiceCategory.query.all()
        return render_template("/ServiceProfessional/register.html", Categories=categories)
    elif user_type=="professional" and request.method=="POST":
        sfname = request.form.get("sf_name")
        sfemail = request.form.get("sf_email")
        sfphone = request.form.get("sf_phone")
        sfcity = request.form.get("sf_city")
        sfexperience=request.form.get("sf_experience")
        sfcategoryid=request.form.get("sf_category")
        sfpassword = request.form.get("sf_password")
        sfaddress = request.form.get("sf_address")
        resume=request.files["sf_resume"]

        Profess = Professional.query.filter_by(email=sfemail).first()
        if Profess:
            flash("Email Id already exist!! user different Email Insted")
            return redirect("/register/customer")
        else:
            path = './static/resume/'
            if not os.path.exists(path):
                os.makedirs(path)
            filename = secure_filename(resume.filename)
            resume_path = os.path.join(path, f"{sfemail}_{filename}")
            resume.save(resume_path)
            newprofess=Professional(name=sfname,email=sfemail,phone=sfphone,city=sfcity,experience=sfexperience,status="Requested", password=sfpassword,address=sfaddress,category_id=sfcategoryid,resume=resume_path[1:])
            db.session.add(newprofess)
            db.session.commit()
            flash("Your profile has been created")
            return redirect("/login")

#login Route
@app.route("/login", methods=["GET", "POST"]) 
def Login():
    if request.method=="POST":
        email=request.form.get("email")    
        pwd=request.form.get("password") 
        loguser=User.query.filter_by(email=email).first() or \
        Professional.query.filter_by(email=email).first() or \
        Admin.query.filter_by(email=email).first()
        if loguser and loguser.password==pwd:
            if isinstance(loguser,User):
                login_user(loguser)
                print("cooki saved")
                return redirect('/dashboard')
            elif isinstance(loguser,Professional):
                login_user(loguser)
                return redirect("/dashboard")
            elif isinstance(loguser,Admin):
                login_user(loguser)
                return redirect("/dashboard")
    return render_template("login.html")    

@app.route("/dashboard/profile-setting",methods=["GET","POST"])  
def profile_setting():
    
    if request.method=="GET" and isinstance(current_user,Admin):
        return render_template("/Admin/profilesetting.html",cu=current_user)
    
    elif request.method=="GET" and isinstance(current_user,User):
        return render_template("/Customer/profilesetting.html",cu=current_user)
    elif request.method=="GET" and isinstance(current_user,Professional):
        return render_template("/ServiceProfessional/profilesetting.html",cu=current_user)
    elif request.method=="POST" and  isinstance(current_user,Admin):
        
        cu=current_user
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        if name:
            cu.name=name
        if email:
            cu.email=email
        if password:
            cu.password=password
        db.session.commit()
        return redirect("/dashboard/profile-setting")
    elif request.method=="POST" and isinstance(current_user,Professional):
        cu=current_user
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        city = request.form.get("city")
        password = request.form.get("password")
        address = request.form.get("address")
        if name:
            cu.name=name
        if email:
            cu.email=email
        if phone:
            cu.name=phone
        if city:
            cu.city=city
        if password:
            cu.name=password
        if address:
            cu.address=address
        db.session.commit()
        return redirect("/dashboard/profile-setting")
    elif request.method=="POST" and isinstance(current_user,User):
        cu=current_user
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        city = request.form.get("city")
        password = request.form.get("password")
        address = request.form.get("address")
        if name:
            cu.name=name
        if email:
            cu.email=email
        if phone:
            cu.name=phone
        if city:
            cu.city=city
        if password:
            cu.name=password
        if address:
            cu.address=address
        db.session.commit()
        return redirect("/dashboard/profile-setting")
    


def paginate_query_admin(model, status, per_page=5):
    all_records = model.query.filter_by(status=status).all()
    return [all_records[i:i + per_page] for i in range(0, len(all_records), per_page)]

def paginate_query_professional(model, status, id, per_page=5):
    if len(status)==2:
        all_records = model.query.filter(or_(model.status == status[0], model.status == status[1]),model.professional_id == id).all()
        return [all_records[i:i + per_page] for i in range(0, len(all_records), per_page)]
    else:
        all_records = model.query.filter_by(status=status[0],professional_id= id).all()
        return [all_records[i:i + per_page] for i in range(0, len(all_records), per_page)]
def paginate_query_customer(model, status, id, per_page=5):
    if len(status)==2:
        all_records = model.query.filter(or_(model.status == status[0], model.status == status[1]),model.customer_id == id).all()
        return [all_records[i:i + per_page] for i in range(0, len(all_records), per_page)]
    else:
        all_records = model.query.filter_by(status=status[0],customer_id= id).all()
        return [all_records[i:i + per_page] for i in range(0, len(all_records), per_page)]

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def Dashboard():
    if isinstance(current_user,User):
        if request.method=="GET":
            cu=current_user
            categories=ServiceCategory.query.all()
            paginated_open_bookings=paginate_query_customer(Booking,["Open","Done"],cu.id)
            paginated_requested_bookings=paginate_query_customer(Booking,["Requested"],cu.id)
            paginated_closed_bookings=paginate_query_customer(Booking,["Closed","Finished"],cu.id)
            print(paginated_open_bookings)
            return render_template("/Customer/dashboard.html",cu=current_user,categories=categories,paginated_open_bookings=paginated_open_bookings,
                                   paginated_requested_bookings=paginated_requested_bookings,paginated_closed_bookings=paginated_closed_bookings)
    elif isinstance(current_user,Professional):
        if request.method=="GET":
            cu=current_user
            paginated_open_bookings=paginate_query_professional(Booking,["Open","Done"],cu.id)
            paginated_requested_bookings=paginate_query_professional(Booking,["Requested"],cu.id)
            paginated_closed_bookings=paginate_query_professional(Booking,["Closed","Cancelled"],cu.id)
            return render_template("/ServiceProfessional/dashboard.html",cu=cu,paginated_open_bookings=paginated_open_bookings,paginated_requested_bookings=paginated_requested_bookings,paginated_closed_bookings=paginated_closed_bookings)
    elif isinstance(current_user,Admin):
        if request.method=="GET":
            categories=ServiceCategory.query.all()
            paginated_professional = paginate_query_admin(Professional,"Active")
            paginated_req_professional = paginate_query_admin(Professional,"Requested")
            paginated_blocked_professional = paginate_query_admin(Professional,"Blocked")
            paginated_customer = paginate_query_admin(User,"Active")
            paginated_blocked_customer = paginate_query_admin(User,"Blocked")
            
            return render_template("/Admin/dashboard.html",cu=current_user,categories=categories,
                                   paginated_professional=paginated_professional,paginated_req_professional=paginated_req_professional,
                                   paginated_blocked_professional=paginated_blocked_professional,paginated_customer=paginated_customer,
                                   paginated_blocked_customer=paginated_blocked_customer)

@app.route("/dashboard/search", methods=["GET", "POST"])
@login_required
def admin_search():
    if request.method=="GET":
        return render_template("/Admin/search.html" , cu=current_user)
    elif request.method=="POST":
        
        username=request.form.get("username")
        u=request.form.get("u")
        if u=="customer":
            
            user= User.query.filter(User.name.like(f"%{username}%")).first()
            
        elif u=="professional":
            user= Professional.query.filter(Professional.name.like(f"%{username}%")).first()
            print(user)
    return render_template("/Admin/search.html" , cu=current_user,user=user,method="post",u=u)
            
#Admin will see service catogories
@app.route("/dashboard/service-categories", methods=["GET", "POST"])
@login_required
def admin_services():
    if request.method=="GET" and len(request.args)==0:
        categories=ServiceCategory.query.all()
        return render_template("/Admin/services.html",cu=current_user,categories=categories)
    elif request.method=="GET" and request.args.get("intent")=="delete":
        id=request.args.get("catid")
        categori=ServiceCategory.query.filter_by(id=id).first()
        db.session.delete(categori)
        db.session.commit()
        return redirect("/dashboard/service-categories")
    elif request.method=="POST" and request.args.get("intent")=="create":
        name=request.form.get("categoryname")
        price=request.form.get("initialprice")
        tags=request.form.get("categorytags")
        catimg=request.files["categoryimage"]
        folder_path="./static/category/"
        
        path = './static/category/'
        
        filename = secure_filename(catimg.filename)
        img_path = os.path.join(path, filename)
        catimg.save(img_path)
        newcategory=ServiceCategory(name=name,base_price=price,tags=tags,img_url=img_path[1:])
        db.session.add(newcategory)
        db.session.commit()
        return redirect("/dashboard/service-categories")
    elif request.method=="POST" and request.args.get("intent")=="change":
        name=request.form.get("categoryname")
        price=request.form.get("initialprice")
        
        tags=request.form.get("categorytags")
        catimg=request.files["categoryimage"]
        catid = request.args.get("catid")
        categori= ServiceCategory.query.filter_by(id=catid).first()
        folder_path="./static/serviceplan/"
        img_path=folder_path+f"{catimg}.png"
        if categori: 
            if name:
                categori.name=name
            if tags:
                categori.tags=tags
            if price:
                categori.base_price=price
            if catimg:
                path = '.'+categori.img_url
                catimg.save(path)
        db.session.commit()
        return redirect("/dashboard/service-categories")
        

#Admin can see Professional
@app.route("/dashboard/professional-detail/<int:id>", methods=["GET", "POST"])
@login_required
def professional_detail(id):
    if request.method=="GET" and len(request.args)==0:
        prof = Professional.query.filter_by(id = id).first()
        return render_template("/Admin/professional-detail.html",cu=current_user,professional=prof)
    elif request.method=="GET" and request.args.get("intent")=="Reject":
        prof = Professional.query.filter_by(id = id).first()
        prof.status = "Rejected"
        db.session.commit()
        return redirect(f"/dashboard/professional-detail/{id}")
    elif request.method=="GET" and request.args.get("intent")=="Accept":
        prof = Professional.query.filter_by(id = id).first()
        prof.status = "Active"
        db.session.commit()
        return redirect(f"/dashboard/professional-detail/{id}")
    elif request.method=="GET" and request.args.get("intent")=="Block":
        prof = Professional.query.filter_by(id = id).first()
        prof.status = "Blocked"
        db.session.commit()
        return redirect(f"/dashboard/professional-detail/{id}")
    elif request.method=="GET" and request.args.get("intent")=="UnBlock":
        prof = Professional.query.filter_by(id = id).first()
        prof.status = "Active"
        db.session.commit()
        return redirect(f"/dashboard/professional-detail/{id}")

@app.route("/dashboard/customer-detail/<int:id>", methods=["GET", "POST"])
@login_required
def customer_detail(id):
    print(request.method)
    print(id)
    if request.method=="GET" and len(request.args)==0:
        customer = User.query.filter_by(id = id).first()
        return render_template("/Admin/customer-detail.html",cu=current_user,customer=customer)
    elif request.method=="GET" and request.args.get("intent")=="Block":
        print("i am here")
        customer = User.query.filter_by(id = id).first()
        customer.status="Blocked"
        db.session.commit()
        return redirect(f"/dashboard/customer-detail/{id}")
    elif request.method=="GET" and request.args.get("intent")=="Unblock":
        customer = User.query.filter_by(id = id).first()
        customer.status="Active"
        db.session.commit()
        return redirect(f"/dashboard/customer-detail/{id}")



@app.route("/dashboard/serviceplans", methods=["GET", "POST"])
@login_required
def serviceplans():
    if request.method=="GET":
        return render_template("/ServiceProfessional/serviceplans.html",cu=current_user)
    elif request.method=="POST" and request.args.get("planid")!=None:
        planid=request.args.get("planid")
        pname=request.form.get("planname")
        pprice=request.form.get("planprice")
        pdesc=request.form.get("plandescription")
        ptags=request.form.get("plantags")
        pimage=request.files["planimage"]
        plan = ServicePlan.query.filter_by(id=planid).first()

        if plan: 
            if pname:
                plan.name=pname
            if ptags:
                plan.tags=ptags
            if pprice:
                plan.price=pprice
            if pname:
                plan.desc=pdesc
            if pimage:
                path = '.'+plan.planimg
                pimage.save(path)
        db.session.commit()
        return redirect("/dashboard/serviceplans")
    elif request.method=="POST" and len(request.args)==0:
        sfid=current_user.id
        pname=request.form.get("planname")
        pprice=request.form.get("planprice")
        ptags=request.form.get("plantags")
        pdesc=request.form.get("plandescription")
        pimage=request.files["planimage"]
        category_id=current_user.category_id
        folder_path="./static/serviceplan/"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        img_path=folder_path+f"{pname}.png"
        if pimage and pimage.filename.lower().endswith('.png'):
            pimage.save(img_path)
        newplan=ServicePlan(name=pname,tags=ptags,price=pprice,category_id=category_id,description=pdesc,professional_id=sfid,planimg=img_path[1:])
        db.session.add(newplan)
        db.session.commit()
        return redirect("/dashboard/serviceplans")
    


@app.route("/dashboard/<cat_name>", methods=["GET", "POST"])
def search(cat_name):
    if request.method=="GET" and isinstance(current_user,User):
        categorie=ServiceCategory.query.filter_by(name=cat_name).first()
        return  render_template("/Customer/Book-plan.html",cu=current_user,cat=categorie)
    elif request.method=="POST" and len(request.args)==0:
        tagname=request.form.get("tag")
        categorie=ServiceCategory.query.filter_by(name=cat_name).first()
        plans = db.session.query(ServicePlan).join(
        Professional, ServicePlan.professional_id == Professional.id).filter(
                ServicePlan.tags.ilike(f"%{tagname}%"),
                Professional.city.ilike(f"%{current_user.city}%") 
        ).all()
        plans=ServicePlan.query.filter(ServicePlan.tags.ilike(f"%{tagname}%")).all()
        return render_template("/Customer/Book-plan.html",cu=current_user,cat=categorie,plans=plans,method="POST")


@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method=="POST" and request.args["intent"]=="book":
        cu=current_user
        planid=request.args.get("planid")
        cat_id=request.args.get("catid")
        profid=request.args.get("profid")
        bdate=request.form.get("bdate")
        btime=request.form.get("btime")
        if request.form.get("addressChoice")=="bdefault":
            baddress=cu.address
        else:
            baddress=request.form.get("baddress")
        booking= Booking(professional_id=profid,customer_id=cu.id,category_id=cat_id,service_plan_id=planid,date=bdate,time=btime,address=baddress,status="Requested")
        db.session.add(booking)
        db.session.commit()
        
        return redirect("/dashboard")
    elif request.method=="GET" and request.args.get("intent")=="Accept" and isinstance(current_user,Professional):
        bid=int(request.args.get("bid"))
        booking=Booking.query.filter_by(id=bid).first()
        booking.status="Open"
        db.session.commit()
        return redirect(f"/dashboard/booking/{bid}")
    elif request.method=="GET" and request.args.get("intent")=="Decline" and isinstance(current_user,Professional):
        bid=int(request.args.get("bid"))
        booking=Booking.query.filter_by(id=bid).first()
        booking.status="Declined"
        db.session.commit()
        return redirect(f"/dashboard/booking/{bid}")
    elif request.method=="GET" and request.args.get("intent")=="Cancel" and isinstance(current_user,User):
        bid=int(request.args.get("bid"))
        booking=Booking.query.filter_by(id=bid).first()
        booking.status="Cancelled"
        db.session.commit()
        return redirect(f"/dashboard/booking/{bid}")
    elif request.method=="GET" and request.args.get("intent")=="Done" and isinstance(current_user,Professional):
        bid=int(request.args.get("bid"))
        booking=Booking.query.filter_by(id=bid).first()
        booking.status="Done"
        db.session.commit()
        return redirect(f"/dashboard/booking/{bid}")
    elif request.method=="POST" and request.args.get("intent")=="close" and isinstance(current_user,User):
        bid=int(request.args.get("bid"))
        brating=int(request.form.get("rating"))
        rmessage=request.form.get("rmessage")
        booking=Booking.query.filter_by(id=bid).first()
        booking.rating=brating
        booking.ratingmessage=rmessage
        print("if")
        if brating == 5:
            
            booking.remark = "Excellent Service"
        if 2 < brating <5:
            print("if here")
            booking.remark = "Good Service"
        else:
            booking.remark = "Poor Service"


        booking.status="Closed"
        db.session.commit()
        return redirect(f"/dashboard/booking/{bid}")

@app.route("/dashboard/booking/<int:id>", methods=["GET", "POST"])
def booking_detail(id):
    if request.method=="GET":
        cu=current_user
        if isinstance(cu,User):
            booking = Booking.query.filter_by(id=id).first()
            return render_template("/customer/Booking-detail.html",booking=booking,cu=current_user)
        elif isinstance(cu,Professional):
            booking = Booking.query.filter_by(id=id).first()
            print(f"this is booking:{booking}")
            return render_template("/ServiceProfessional/Booking-detail.html",booking=booking,cu=current_user)

def stats(method,cu,model,id):
    if method=="GET":
        if cu=="professional":
            bookings = model.query.filter_by(professional_id= id).all()
        elif cu=="admin":
            bookings = model.query.all()
        elif cu=="customer":
            bookings = bookings = model.query.filter_by(customer_id= id).all()
        status_count = {"Requested": 0, "Open": 0, "Cancelled": 0, "Closed": 0}
        for booking in bookings:
            if booking.status in status_count:
                status_count[booking.status] += 1
        call=requests.get("http://127.0.0.1:5000/api/extractstats",json={"status_count":status_count,"cu":cu,"m":method})
        return call
    elif method=="POST":
        if cu=="professional":
            ser_plan=ServicePlan.query.filter_by(id=id).first()
            specific=ser_plan.name
            bookings = model.query.filter_by(service_plan_id= id).all()
        elif cu=="admin":
            ser_cat=ServiceCategory.query.filter_by(id=id).first()
            specific=ser_cat.name
            bookings = model.query.filter_by(category_id= id).all()
        status_count = {"Requested": 0, "Open": 0, "Cancelled": 0, "Closed": 0}
        for booking in bookings:
            if booking.status in status_count:
                status_count[booking.status] += 1
        call=requests.get("http://127.0.0.1:5000/api/extractstats",json={"status_count":status_count,"cu":cu,"m":method,"specific":specific})
    
        return call




@app.route("/dashboard/statistics", methods=["GET", "POST"])
def statistics():
    print(f"method is  {request.method}")
    if request.method=="GET" and isinstance(current_user,Professional):
        cu="professional"
        id=current_user.id
        call = stats("GET",cu,Booking, id )
        if call.status_code==200:
            return render_template("/ServiceProfessional/statistics.html",cu=current_user,path=call.json()["path"])
        else:
            return render_template("/ServiceProfessional/statistics.html",cu=current_user,path="Not available")
    elif request.method=="POST" and isinstance(current_user,Professional):
        cu="professional"
        id=request.form.get("planid")
        call = stats("POST",cu,Booking,id)
        if call.status_code==200:
            return render_template("/ServiceProfessional/statistics.html",cu=current_user,path=call.json()["path"])
        else :
            print(call.status_code)
            return render_template("/ServiceProfessional/statistics.html",cu=current_user,path="Not available")
    elif request.method=="GET" and isinstance(current_user,Admin):
        cu="admin"
        id=current_user.id
        call = stats("GET",cu,Booking, id )
        all_ser_cat=ServiceCategory.query.all()
        if call.status_code==200:
            return render_template("/Admin/statistics.html",cu=current_user,path=call.json()["path"],all_ser=all_ser_cat)
        else:
            return render_template("/Admin/statistics.html",cu=current_user,path="Not available",all_ser=all_ser_cat)
    elif request.method=="POST" and isinstance(current_user,Admin):
        cu="admin"
        id=request.form.get("catid")
        print(id)
        call = stats("POST",cu,Booking, id )
        all_ser_cat=ServiceCategory.query.all()
        if call.status_code==200:
            return render_template("/Admin/statistics.html",cu=current_user,path=call.json()["path"],all_ser=all_ser_cat)
        else:
            return render_template("/Admin/statistics.html",cu=current_user,path="Not available",all_ser=all_ser_cat)
    if request.method=="GET" and isinstance(current_user,User):
        cu="customer"
        id=current_user.id
        call = stats("GET",cu,Booking, id )
        if call.status_code==200:
            return render_template("/Customer/statistics.html",cu=current_user,path=call.json()["path"])
        else:
            return render_template("/Customer/statistics.html",cu=current_user,path="Not available")
        
    
@app.route("/logout" ,methods=["GET", "POST"])
@login_required
def log_out():
    logout_user()
    return redirect("/login")