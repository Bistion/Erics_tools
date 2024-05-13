from flask import Flask, render_template, request
from dotenv import load_dotenv
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

from views import views

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")

# SQLAlchemy database setup
# load_dotenv()
# TURSO_DATABASE_URL= os.getenv("TURSO_DATABASE_URL")
# TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
# dbUrl = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"
# engine = create_engine(dbUrl, connect_args={'check_same_thread': False}, echo=True)
#engine = create_engine(f"sqlite:///New_System_Scans.db", echo=False)

# session = scoped_session(
#   sessionmaker(
#     autoflush=False,
#     autocommit=False,
#     bind=engine
#   )
# )

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
  cursor = dbapi_connection.cursor()
  cursor.execute("PRAGMA foreign_keys=ON")
  cursor.close()



if __name__ == '__main__':
  app.run(debug=True, port=8000 )