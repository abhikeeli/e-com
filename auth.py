from flask import Blueprint, request, make_response, session, render_template, redirect, url_for, current_app
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models import User
from db import db

auth=Blueprint("auth",__name__,template_folder="templates")

def tokenchecker():
    token = request.cookies.get('token')
    if(token):
        try:
            payload=jwt.decode(token,current_app.config['SECRET_KEY'],algorithms='HS256',salt_length=8)
            session['username']=payload['username']
            session['role']=payload['role']
        except jwt.ExpiredSignatureError:
                session['username']=None
                session['role']=None
                return 1
        except jwt.InvalidTokenError:
                session['username']=None
                session['role']=None
                return 1
        return 1
        

            


def role_required(roles):
    def decorator(fun):
        @wraps(fun)
        def wrapped(*args,**kwargs):
            token = request.cookies.get('token')  
            if not token:
                return make_response('no permission',403)
            try:
                payload=jwt.decode(token,current_app.config['SECRET_KEY'],algorithms='HS256',salt_length=8)
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

@auth.route('/signup',methods=['POST','GET'])
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

@auth.route('/login',methods=['GET','POST'])
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
            token=jwt.encode({'username':result.user_name,'role':result.role,'exp':datetime.utcnow()+timedelta(days=1),'user_id':result.user_id},current_app.config['SECRET_KEY'],algorithm='HS256')
            response=make_response(redirect(url_for('main.index')))
            response.set_cookie('token',token,httponly=True,max_age=86400)
            session["username"] = result.user_name
            session["role"]=result.role
            return response
        else:
            return make_response('unableto authenticate',   403,{'www-Authenticate': 'Basicrealm:"Authentication Failed!"'})
    return render_template('login.html')


@auth.route('/logout')
@role_required(['Merchant','buyer'])
def logout(current_user):
    current_user=None
    session['username']=None
    response=make_response(redirect(url_for('main.index')))
    response.set_cookie('token','',expires=0,httponly=True)
    return response