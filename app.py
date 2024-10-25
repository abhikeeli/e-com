from flask import Flask,request,render_template,make_response,redirect,url_for,session
from db import db, db_init
from models import User,Product
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from datetime import datetime,timedelta
import os
from functools import wraps 
import uuid

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SECRET_KEY']='mandhitenalirasamiiiiiiabbbbhi'
db_init(app)


def role_required(roles):
    def decorator(fun):
        @wraps(fun)
        def wrapped(*args,**kwargs):
            token = request.cookies.get('token')  
            if not token:
                return make_response('no permission',403)
            try:
                payload=jwt.decode(token,app.config['SECRET_KEY'],algorithms='HS256',salt_length=8)
                current_user=payload['user_id']
                if not payload['role'] in roles:
                    return make_response('no permission',403)
            except jwt.ExpiredSignatureError:
                session['username']=None
                return make_response('session expired',401)
            except jwt.InvalidTokenError:
                session['username']=None
                return make_response('forbidden',403)
            return fun(current_user=current_user,*args,**kwargs)
        return wrapped
    return decorator


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        name=request.form.get('fullname')
        user_name=request.form.get('username')
        password=request.form.get('password')
        role=request.form.get('role')
        repassword=request.form.get('repassword')
        if (password!=repassword):
            return render_template("error.html")
        pw_hash=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user=User(full_name=name,user_name=user_name,password=pw_hash,role=role)
        try:
            db.session.add(new_user)
            db.session.commit()
        except:
            return render_template("error.html", message="Username already exists!")
        return render_template("login.html", msg="Account created!")

    return render_template("signup.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        user_name=request.form.get('username')
        password=request.form.get('password')
        result = User.query.filter_by(user_name=user_name).first()
        if result==None:
            return render_template("error.html", message="Username not exists!")
        if not check_password_hash(result.password,password):
            return render_template("error.html", message="Username and  password not macthing")
        if check_password_hash(result.password,password):
            token=jwt.encode({'username':result.user_name,'role':result.role,'exp':datetime.utcnow()+timedelta(days=1),'user_id':result.user_id},app.config['SECRET_KEY'],algorithm='HS256')
            response=make_response(redirect(url_for('index')))
            response.set_cookie('token',token,httponly=True,max_age=86400)
            session["username"] = result.user_name
            session["role"]=result.role
            return response
        else:
            return make_response('unableto authenticate',   403,{'www-Authenticate': 'Basicrealm:"Authentication Failed!"'})
    return render_template('login.html')

@app.route('/')
def index(user=None):
    user=session.get('username')
    role=session.get('role')
    rows = Product.query.all()
    return render_template('index.html',rows=rows,user=user,role=role)

@app.route('/home',methods=['GET','POST'])
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

@app.route("/edit/<int:pro_id>",methods=["GET", "POST"], endpoint='edit')
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
    
@app.route('/logout')
@role_required(['Merchant','buyer'])
def logout(current_user):
    current_user=None
    session['username']=None
    response=make_response(redirect(url_for('index')))
    response.set_cookie('token','',expires=0,httponly=True)
    return response








       



        






