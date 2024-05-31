from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import pandas as pd
import numpy as np
import os, xmltodict, math, requests
from models.base import Base

engine = create_engine(f"sqlite:///swc_info.db", echo=False)
projEngine = create_engine(f"sqlite:///projects.db", echo=False)

def entity_info(searchName):
  pass

def get_hyperlanes(system):
  with engine.connect() as conn:
    clean_system = system.replace("'","''")
    href = pd.read_sql(f"SELECT * FROM 'system_info' WHERE system_name == '{clean_system}'", conn)
  h = {'Accept': 'application/json'}
  res = requests.get(href.system_href.loc[href.index[0]], headers=h).json()
  hl_coords = []
  try:
    for hyperlane in res['swcapi']['system']['hyperlanes']['hyperlane']:
      dest_name = hyperlane['value'].replace(f"{res['swcapi']['system']['name']} to", "").replace(" Hyperlane", "").strip()
      hl_coords.append(f"{hyperlane['attributes']['destinationX']},{hyperlane['attributes']['destinationY']},{dest_name},{hyperlane['attributes']['modifier']}")
  except:
    print(f"No hyperlanes in {system}")
  return hl_coords

def calculate_eta(total, hs, piloting, hl):
  if hl < 0 or math.isnan(hl):
    hl = 0
  if hl > 100:
    hl = 99.999
  hl = 1 - (hl / 100)
  speed = hs * (1.0 + piloting * 0.05)
  interval = math.floor((2 * 60 * 60) * (1 / speed)) # time to go one square
  seconds = math.ceil(total * interval) * hl
  return seconds

def display_eta(seconds):
  mins = seconds / 60
  days  = math.floor(mins / (24 * 60))
  mins = mins % (24 * 60)
  hours = math.floor(mins / (60))
  mins = math.floor(mins % (60))

  # display it
  display = []
  if(days > 1):
    display.append(f"{days} days")
  elif days > 0:
    display.append(f"{days} day")
  if hours > 1:
    display.append(f"{hours} hours")
  elif hours > 0:
      display.append(f"{hours} hour")
  if mins == 0 and len(display) == 0:
    display.append("None")
  elif mins != 1:
    display.append(f"{mins} mins")
  else:
      display.append(f"{mins} min")
  # s = ", "
  # print(f"Travel Time: {s.join(display)}")
  s = ", "
  return s.join(display)

def calc_hyperlane(startSystem,box,pathsDF,path,startX,startY,endX,endY,hs,piloting,initialSystem,seconds,checked_lanes):
  hl_coords = get_hyperlanes(startSystem)
  if len(hl_coords) == 0:
    print("No Hyperlanes Found")
    return
  else:
    for hyperlane in hl_coords:
      sysName = hyperlane.split(",")[2]
      if sysName == initialSystem:
        hl_val = float(hyperlane.split(",")[3])
        total = max(abs(startX - endX), abs(startY - endY))
        newSeconds = calculate_eta(total, hs, piloting, hl_val)
        path += f"->{sysName}"
        print(path)
        seconds += newSeconds
        pathsDF.loc[len(pathsDF.index)] = [f"{path}",startSystem,f"{startX}, {startY}",sysName,f"{endX}, {endY}",newSeconds,display_eta(newSeconds),hl_val,seconds,display_eta(seconds)]
        return
    for hyperlane in hl_coords:
      in_box = 0
      newStartX, newStartY = int(hyperlane.split(",")[0]),int(hyperlane.split(",")[1]) 
      point = Point(newStartX,newStartY)
      polygon = Polygon(box)
      sysName = hyperlane.split(",")[2]
      if polygon.contains(point):
        in_box +=1
        if sysName not in checked_lanes:
          checked_lanes.append(sysName)
          hl_val = float(hyperlane.split(",")[3])
          total = max(abs(startX - newStartX), abs(startY - newStartY))
          newSeconds = calculate_eta(total, hs, piloting, hl_val)
          path += f"->{sysName}({hl_val})"
          seconds += newSeconds
          # hl_coords = get_hyperlanes(sysName)
          pathsDF.loc[len(pathsDF.index)] = [f"{path}",startSystem,f"{startX}, {startY}",sysName,f"{newStartX}, {newStartY}",newSeconds,display_eta(newSeconds),hl_val,seconds,display_eta(seconds)]
          newBox = [[newStartX+30, newStartY-30],[endX+30, endY-30],[endX-30, endY+30],[newStartX-30, newStartY+30]]
          calc_hyperlane(sysName,newBox,pathsDF,path,newStartX,newStartY,endX,endY,hs,piloting,initialSystem,seconds,checked_lanes)
  if in_box == 0:
    # No hyperlane paths from current system to destination
    # Need to figure out reversing this from the destination to the endpoint here.  Then connect the two endpoints found
    hl_val = 0
    sysName = initialSystem
    total = max(abs(startX - endX), abs(startY - endY))
    newSeconds = calculate_eta(total, hs, piloting, hl_val)
    path += f"->{sysName}({hl_val})"
    seconds += newSeconds
    pathsDF.loc[len(pathsDF.index)] = [f"{path}",startSystem,f"{startX}, {startY}",sysName,f"{endX}, {endY}",newSeconds,display_eta(newSeconds),hl_val,seconds,display_eta(seconds)]

def project_estimate(entityType,entityClass,entityName,entityQty):
  if entityQty == "":
    entityQty = 1
  weapons = ["Projectile","Heavy Projectile","Non-Projectile"]
  if entityClass in weapons:
    entityType = "item"
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

def get_sector_list():
  with engine.connect() as conn:
    results = pd.read_sql(f"SELECT sector_name FROM 'system_info' GROUP by sector_name", conn)
  sectorJson = results.to_json(orient='records')
  return sectorJson

def get_system_list():
  with engine.connect() as conn:
    results = pd.read_sql(f"SELECT * FROM 'system_info'", conn)
  systemJson = results.to_json(orient='records')
  return systemJson

def calc_hyperjump(startSystem, endSystem, hs, piloting, hl_val):
  hs, piloting = int(hs), int(piloting)
  with engine.connect() as conn:
    startResults = pd.read_sql(f"SELECT * FROM 'system_info' WHERE system_name == '{startSystem}'", conn)
    endResults = pd.read_sql(f"SELECT * FROM 'system_info' WHERE system_name == '{endSystem}'", conn)
  pathsDF = pd.DataFrame(columns=['Path','From System Name','From System Coords','To System Name','To System Coords','ETA Seconds','ETA Calculated','HL Value','Combined Seconds','Combined ETA'])
  initialX = startResults.x_coord.loc[startResults.index[0]]
  initialY = startResults.y_coord.loc[startResults.index[0]]
  endX = endResults.x_coord.loc[endResults.index[0]]
  endY = endResults.y_coord.loc[endResults.index[0]]
  box = [[initialX+30, initialY-30],[endX+30, endY-30],[endX-30, endY+30],[initialX-30, initialY+30]]
  print(box)
  path = f"{startSystem}"
  seconds = 0
  checked_lanes = []
  calc_hyperlane(startSystem,box,pathsDF,path,initialX,initialY,endX,endY,hs,piloting,endSystem,seconds,checked_lanes)

  fullPathsDF = pathsDF.loc[pathsDF['To System Name'] == f"{endSystem}"]
  fullPathsDF = fullPathsDF.sort_values(by=['Combined Seconds'],ignore_index=True).head()
  total = max(abs(initialX - endX), abs(initialY - endY))
  seconds = calculate_eta(total, hs, piloting, hl_val)
  directDF = pd.DataFrame([['Direct Route',display_eta(seconds)]],columns=['Path','Combined ETA'])
  fullPathsDF = fullPathsDF.loc[:,['Path','Combined ETA']]
  fullPathsDF = pd.concat([directDF, fullPathsDF])
  fullPathsDF = fullPathsDF.reset_index()
  for index, row in fullPathsDF.iterrows():
    print(row['Path'],row['Combined ETA'])
  print(f"Pathing from {startSystem} to {endSystem} found:\n{fullPathsDF}")
  return fullPathsDF