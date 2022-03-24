from flask import Flask, render_template,request,session
import sqlite3
import werkzeug
from flask_login import loginManager, login_required
from flask_sqlalchemy import SQLAlchemy
