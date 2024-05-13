from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Relationship

from models.base import TimeStampedModel, Model

class Entity(TimeStampedModel):
  __tablename__ = "Entity Changes"

  id = Column(Integer, primary_key=True, autoincrement=True)
  entityID = Column(Integer, nullable=False) #nullable means required field
  name = Column(String(120), nullable=False)
  last_seen = Column(String(80), nullable=False)
  typeName = Column(String(80), nullable=False)
  system = Column(String(80), nullable=False)

  def __repr__(self):
    return f"{self.__class__.__name__}, name: {self.entity_name} entityId: {self.entity_id} name changed on: {self.name_changed}"
  
class File(TimeStampedModel):
  __tablename__ = "Processed Files"

  id = Column(Integer, primary_key=True, autoincrement=True)
  file_name = Column(Integer, nullable=False) #nullable means required field
  scan_date = Column(String(120), nullable=False)
  system = Column(String(80), nullable=False)

  def __repr__(self):
    return f"{self.__class__.__name__}, name: {self.entity_name} entityId: {self.entity_id} name changed on: {self.name_changed}"