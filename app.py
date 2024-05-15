from flask import Flask
from sqlalchemy.engine import Engine
from sqlalchemy import event, create_engine
import os

from views import views

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["TEMPLATES_AUTO_RELOAD"] = True

engine = create_engine(f"sqlite:////var/data/System_Scans.db", echo=False)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
  cursor = dbapi_connection.cursor()
  cursor.execute("PRAGMA foreign_keys=ON")
  cursor.close()

if __name__ == '__main__':
  # app.run(debug=True, port=8000 )
  app.run(debug=True)