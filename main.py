from flask import session,Blueprint,render_template,request
import os
import uuid
from models import Product
from db import db
from auth import role_required,tokenchecker

main=Blueprint("main",__name__,template_folder="templates")

@main.route('/')
def index(user=None):
    tokenchecker()
    user=session.get('username')
    role=session.get('role')
    print(user)
    print(role)
    rows = Product.query.all()
    return render_template('index.html',rows=rows,user=user,role=role)

@main.route('/home',methods=['GET','POST'])
@role_required(['Merchant'])
def home(current_user):
   if (request.method=="POST"):
       image=request.files['image']
       filename = str(uuid.uuid1())+os.path.splitext(image.filename)[1]
       image.save(os.path.join("static/images", filename))
       product_name=request.form.get('pro_name')
       description=request.form.get('description')
       price_range=request.form.get('price_range')
       comments=request.form.get('comments')
       merchant_id = current_user


       new_pro=Product(product_name=product_name,merchant_id=merchant_id,description=description,price_range=price_range,comments=comments,filename=filename)
       db.session.add(new_pro)
       db.session.commit()
       rows = Product.query.filter_by(merchant_id=current_user)
       return render_template("home.html", rows=rows, message="Product added")
   rows = Product.query.filter_by(merchant_id=current_user)
   return render_template("home.html",rows=rows)

@main.route("/edit/<int:pro_id>",methods=["GET", "POST"], endpoint='edit')
@role_required('Merchant')
def edit(pro_id,current_user):
    result = Product.query.filter_by(product_id = pro_id).first()
    if request.method=="POST":
        if result.merchant_id != current_user:
            return render_template("error.html", message="You are not authorized to edit this product")
        name = request.form.get("pro_name")
        description = request.form.get("description")
        price_range = request.form.get("price_range")
        comments = request.form.get("comments")
        result.name = name
        result.description = description
        result.comments = comments
        result.price_range = price_range
        db.session.commit()
        rows = Product.query.filter_by(merchant_id=current_user)
        return render_template("home.html", rows=rows, message="Product edited")
    return render_template("edit.html", result=result)