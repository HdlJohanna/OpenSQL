from flask import Flask, render_template,request,session
import sqlite3
import werkzeug
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_required, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
connections = {}
db = SQLAlchemy(app)
login = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer)
    username = db.Column(db.String(30),unique=True)


@app.route("/")
def main():
    return render_template("index.html")

@app.route("/cluster/0")
@login_required
def clust():
    connections[request.remote_addr] = sqlite3.connect(f'{secure_filename(current_user.username.lower())}.db')

app.run("0.0.0.0",80)