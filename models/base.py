from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

Model = declarative_base()

class TimeStampedModel(Model):
  __abstract__ = True

