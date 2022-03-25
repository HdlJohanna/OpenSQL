from flask import Flask, render_template,request, redirect
import os
import sqlite3
import requests
from flask.helpers import send_from_directory, flash, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user,login_required,current_user, logout_user
import random,string

connections = {}

def getRandomString(length):
    return ''.join(random.choices(string.ascii_letters+string.digits,k=length))

from smtplib import SMTP
smtp = SMTP('smtp.gmail.com:587')
smtp.starttls()
# smtp.login('opensqldb93@gmail.com', 'buchstabe')

# Prepare email
from pymailer import Email
email = Email()
email.server = smtp
app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SECRET_KEY"] = "nuefhniuewfiue"
db = SQLAlchemy(app)
loginManager = LoginManager()
loginManager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30),unique=True)
    email = db.Column(db.String(30),unique=True)
    password = db.Column(db.String(30))
    state = db.Column(db.String(30))
    email_verified = db.Column(db.Integer)


@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register",methods=["GET","POST"])
def regist():
  if request.method == "GET":
    return render_template("register.html")
  else:
    emailad = request.form.get("email")
    username  = request.form.get("username")
    passwd = request.form.get("passwd")
    state = getRandomString(10)
    db.session.add(User(username=username, password=passwd,state=state,email_verified=0))
    db.session.commit()
    email.recipients = [emailad]
    email.subject = 'Verify Yourself'				# optional
    print(f'http://127.0.0.1:5000/account/verify?state={state}&username={username}&password={passwd}')
    email.text = f'Verify your Email Address:\n\nVisit this Link to Authorize Yourself: http://127.0.0.1/account/verify?state={state}&username={username}&password={passwd}'	# optional
    # email.send()
    return render_template("awaitingApprove.html",email=emailad)

@app.route("/account/verify")
def verify():
    state = request.args.get('state')
    username = request.args.get('username')
    password = request.args.get('password')
    u = User.query.filter_by(username=username).first()
    if u.password == password:
        if u.state == state:
            u.query.update({'email_verified':True})
            login_user(u,True)
            conn = sqlite3.connect(f'{secure_filename(u.username.lower())}.db')
            db.session.commit()
            return redirect('/account')
        return "Secret Key does not match!"
    return "Password does not match!"

@app.route('/login',methods=['POST','GET'])
@app.route('/account/login',methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        user = User.query.filter_by(username=request.form.get('username'),password=request.form.get('passwd')).first()
        if user:
            conn = sqlite3.connect(f'{secure_filename(current_user.username.lower())}.db')
            login_user(user)
            return redirect('/account')
        else:
            return render_template("login.html")

@app.route('/account')
@login_required
def me():
    if current_user.email_verified:
        return render_template('dashboard.html',user=current_user)
    return render_template('awaitingApprove.html')

@app.route("/api/sql",methods=["POST"])
def runsql():
    auth = request.headers.get('SECRET_KEY')
    proto, key = auth.split('+')

    state,username = key.split("/")
    user = User.query.filter_by(username=username).first()
    if not user or user.state != state:
        return {"error": "403 Forbidden","fatal": True}
    conn = sqlite3.connect(f'{secure_filename(user.username.lower())}.db')
    cur = conn.cursor()
    try:
        cur.execute(request.headers.get('QUERY_STRING'))
        res = cur.fetchall()
        fail = False
    except Exception as error:
        res = str(error)
        fail = True
    conn.commit()
    conn.close()
    if fail:
        return {"error": res,"fatal": True}
    if len(res) == 1:
        return {"result":res[0]}
    return {"result":res}



if __name__ == '__main__':
    app.run("0.0.0.0",80)
