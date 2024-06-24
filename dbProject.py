from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import pandas as pd
import os, xmltodict, math, requests
from models.base import Base

engine = create_engine(f"sqlite:///swc_info.db", echo=False)
projEngine = create_engine(f"sqlite:///projects.db", echo=False)

def entity_info(searchName):
  pass

def project_estimate(entityType,entityClass,entityName,entityQty):
  if entityQty == "":
    entityQty = 1
  rmWeight = {"quantum":12,"meleenium": 11,"ardanium":8,"rudic":1,"ryll":1,"duracrete":9,"alazhi":2,"laboi":4,"adegan":3,"rockivory":12,"tibannagas":0.16,"nova":2,"varium":10,"varmigio":9,"lommite":6,"hibridium":14,"durelium":8,"lowickan":4,"vertex":4,"berubian":3,"bacta":0.8}
  weapons = ["Projectile","Heavy Projectile","Non-Projectile"]
  if entityClass in weapons:
    entityType = "item"
  tableName = f"{entityType}_info"
  tableName = tableName.lower()
  materialList = f"<h3>Materials required to build {entityQty} x {entityName}.</h3><br/>"
  totalWeight = 0.0
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
          weight = rmWeight[rmSplit[0]] * int(rmSplit[1]) * int(entityQty)
          materialData = f"{rmSplit[0]}: {int(rmSplit[1]) * int(entityQty)}<br/>"
          materialList += materialData
          totalWeight += weight
  totalWeight = f"Total RM Weight: {round(totalWeight, 2)}"
  materialList += totalWeight
  return materialList

def get_entity_list():
  entityDF = pd.DataFrame()
  includeList = ["droid_info", "facility_info", "item_info", "ship_info", "station_info","vehicle_info"]
  with engine.connect() as conn:
    tables = inspect(engine).get_table_names()
    for table in tables:
      if table in includeList:
        results = pd.read_sql(f"SELECT name, class FROM '{table}'", conn)
        entityDF = pd.concat([results,entityDF])
      else:
        pass
  entityDF = entityDF.sort_values(by=['class','name'])
  entityJson = entityDF.to_json(orient='records')
  return entityJson