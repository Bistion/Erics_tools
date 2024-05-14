from flask import Flask, render_template, request
from dotenv import load_dotenv
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

from views import views

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")

# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#   cursor = dbapi_connection.cursor()
#   cursor.execute("PRAGMA foreign_keys=ON")
#   cursor.close()

if __name__ == '__main__':
  app.run(debug=True, port=8000 )