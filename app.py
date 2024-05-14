from flask import Flask
from sqlalchemy.engine import Engine
from sqlalchemy import event
import os

from views import views

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
  cursor = dbapi_connection.cursor()
  cursor.execute("PRAGMA foreign_keys=ON")
  cursor.execute('PRAGMA busy_timeout = 20000')
  cursor.close()

if __name__ == '__main__':
  # app.run(debug=True, port=8000 )
  app.run(host='0.0.0.0', debug=True)