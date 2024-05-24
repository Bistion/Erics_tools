from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
import pandas as pd
import os, xmltodict
from models.base import Base

engine = create_engine(f"sqlite:///swc_info.db", echo=False)
projEngine = create_engine(f"sqlite:///projects.db", echo=False)

def entity_info(searchName):
  pass

def project_estimate(entityType,entityName,entityQty):
  if entityQty == "":
    entityQty = 1
  tableName = f"{entityType}_info"
  tableName = tableName.lower()
  materialList = f"<h3>Materials required to build {entityQty} x {entityName}.</h3><br/>"
  entityName = entityName.replace("'","''").replace(":","\:")
  with engine.connect() as conn:
    rmList = pd.read_sql(f"SELECT materials FROM '{tableName}' WHERE name == '{entityName}'", conn)
    if rmList['materials'].loc[rmList.index[0]] == "No Materials":
      materialList += f"Unique entity with no materials listed"
    else:
      rmList = rmList['materials'].loc[rmList.index[0]].split(",")
      for rm in rmList:
        if rm != "":
          rmSplit = rm.split('-')
          materialData = f"{rmSplit[0]}: {int(rmSplit[1]) * int(entityQty)}<br/>"
          materialList += materialData
  return materialList

def get_entity_list():
  entityDF = pd.DataFrame()
  excludeList = ["creature_info", "entity_info", "npc_info", "weapon_info"]
  with engine.connect() as conn:
    tables = inspect(engine).get_table_names()
    for table in tables:
      if table in excludeList:
        continue
      else:
        results = pd.read_sql(f"SELECT name, class FROM '{table}'", conn)
        entityDF = pd.concat([results,entityDF])
  entityDF = entityDF.sort_values(by=['class','name'])
  entityJson = entityDF.to_json(orient='records')
  return entityJson