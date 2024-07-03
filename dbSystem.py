from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
import pandas as pd
import os, xmltodict
from models.base import Base
from datetime import datetime as dt

engine = create_engine(f"sqlite:////var/data/System_Scans.db", echo=False)
auxEngine = create_engine(f"sqlite:////var/data/System_Movement.db", echo=False)

def add_data(data, system_name, scan_date, item, system_dict):
  scan_data = [system_name,
            scan_date, #actual scan date - static entry that won't change
            scan_date+"(initial entry)", #updated entry for last seen date
            system_dict['rss']['channel']['location']['galX'],
            system_dict['rss']['channel']['location']['galY'],
            item['name'],
            item['typeName'],
            item['entityID'],
            item.get('entityType', 'Unknow Entity Type'),
            f"{item['hull']}/{item['hullMax']}",
            f"{item['shield']}/{item['shieldMax']}",
            f"{item['ionic']}/{item['ionicMax']}",
            item['underConstruction'],
            item['sharingSensors'],
            item['x'],
            item['y'],
            item['travelDirection'],
            item['ownerName'],
            item['iffStatus'],
            item['image'],
            ]
  data.append(scan_data)
  return data

def add_enter_movement(system_name, scan_date, item, system_dict, update_reason):
  scan_data = [system_name,
            scan_date, #actual scan date - static entry that won't change
            system_dict['rss']['channel']['location']['galX'],
            system_dict['rss']['channel']['location']['galY'],
            update_reason,
            item['name'],
            item['typeName'],
            item['entityID'],
            item.get('entityType', 'Unknow Entity Type'),
            f"{item['hull']}/{item['hullMax']}",
            f"{item['shield']}/{item['shieldMax']}",
            f"{item['ionic']}/{item['ionicMax']}",
            item['underConstruction'],
            item['sharingSensors'],
            item['x'],
            item['y'],
            item['travelDirection'],
            item['ownerName'],
            item['iffStatus'],
            item['image'],
            ]
  return scan_data

def add_exit_movement(row, update_reason):
  scan_data = [row[1],
            row[3].replace("(initial entry)",""),
            row[4],
            row[5],
            update_reason,
            row[6],
            row[7],
            row[8],
            row[9],
            row[10],
            row[11],
            row[12],
            row[13],
            row[14],
            row[15],
            row[16],
            row[17],
            row[18],
            row[19],
            row[20]
            ]
  return scan_data

def enter_system_movement(logOutput, movement, system_name):
  df = pd.DataFrame(movement, columns=['system','last_seen','galX','galY', 'update_reason', 'name','typeName','entityID','entityType','hull','shield','ionic','underConstruction','sharingSensors','sysX','sysY','travelDirection','ownerName','iffStatus','image'])
  df.to_sql(name=system_name, con=auxEngine, if_exists='append')
  logOutput += f"### System Movement data has been updated for {system_name}<br/>"

def enter_scan():
  Base.metadata.create_all(engine)
  logOutput = ""
  for root, dirs, files in os.walk(f"/var/data/uploads"):
    for file in files:
      with open(f"/var/data/uploads/{file}", 'r', encoding='ISO-8859-1') as f:
        system_dict = xmltodict.parse(f.read())
        system = system_dict['rss']['channel']['title'].split('Scan of ')
        system_name = system[1]
        scan_date = system_dict['rss']['channel']['lastBuildDate']
        logOutput += "<h3>------------------</h3><br/>"
      with Session(engine) as session:
        with engine.connect() as conn:
          # Continue to next file if coords in the system_name
          if "coords" in system_name:
            logOutput += f"<h3>### File Processing Error!!!! ###</h3><br/>Send the following file to Eric for troubleshooting.<br/>- {file}<br/>"
            os.remove(f"/var/data/uploads/{file}")
            continue 
          data = []
          movement = []
          scanExists = False
          logOutput += f"<h3>{file} dated {scan_date} is being processed</h3><br/>"

          # Check if a table exists
          tblExists = inspect(engine).has_table(f"{system_name}")
          if not tblExists:
            logOutput += f"- No table named {system_name}....<br/>- Table will be created after processing {file} as long as it is successfully processed.<br/>"
          else:
            logOutput += f"- {system_name} Table Exists already.<br/>- Checking if file has already been processed<br/>"
            scanExists = session.execute(text(f"SELECT file_name FROM 'Processed Files' WHERE file_name == '{file}'")).all()
          if scanExists:
            logOutput += f"File already processed----> Skipping.<br/>"
            os.remove(f"/var/data/uploads/{file}")
            continue
          else:
            newestScan = pd.read_sql(f"SELECT system, scan_date FROM 'Processed Files' WHERE system == '{system_name}'", conn)
            newestScan = newestScan.sort_values(by=['scan_date'], ascending=False, ignore_index=True).head(1)
            try:
              compareScan = newestScan['scan_date'].loc[newestScan.index[0]]
              newScanDate = dt.strptime(scan_date, '%a, %d %b %Y %X')
              oldScanDate = dt.strptime(compareScan, '%a, %d %b %Y %X')
              if newScanDate > oldScanDate:
                logOutput += f"Scan date of {scan_date} is newer than last processed scan date of {compareScan}.  Continuing file processing.<br/>"
              else:
                logOutput += f"File Scan date of {scan_date} is older than the newest scan data from {compareScan}.---->Skipping.<br/>"
                os.remove(f"/var/data/uploads/{file}")
                continue
            except:
              pass
          os.remove(f"/var/data/uploads/{file}")
          for item in system_dict['rss']['channel']['item']:
            # Check for Null/blank names
            if item['name'] is None:
              item['name'] = "blank_name"
              entityName = item['name']
            # Checks for ' or : special characters in names.
            else:
              entityName = item['name']
              entityName = entityName.replace("'","''").replace(":","\:")
            if tblExists:
              first_search = session.execute(text(f"SELECT name, entityID FROM '{system_name}' WHERE entityID == '{item['entityID']}' AND name == '{entityName}'")).all()
              if first_search:
                session.execute(text(f"UPDATE '{system_name}' SET last_seen='{scan_date}' WHERE entityID == '{item['entityID']}' AND name == '{entityName}'"))
              else:
                second_search = pd.read_sql(f"SELECT name FROM '{system_name}' WHERE entityID == '{item['entityID']}'", conn)
                if not second_search.empty:
                  logOutput += f"Entity with an ID of {item['entityID']} already entered as {second_search.name.values[0]}, but is now reporting a different name.<br/>Updating name to be {item['name']}<br/>"
                  session.execute(text(f"UPDATE '{system_name}' SET last_seen='{scan_date}', name='{entityName}' WHERE entityID == '{item['entityID']}'"))
                  session.execute(text(f"INSERT INTO 'Entity Changes' (entityID, name, ownerName, last_seen, typeName, system) VALUES ('{item['entityID']}', '{second_search.name.values[0]}', '{item['ownerName']}', '{scan_date}', '{item['typeName']}', '{system[1]}')"))
                  session.commit()
                else:
                  logOutput += f"--> Ship Named: {item['name']} (ID#: {item['entityID']}, Owner: {item['ownerName']}) entered the system.<br/>"
                  data = add_data(data, system_name, scan_date, item, system_dict)
                  update_reason = "Entered System"
                  movement.append(add_enter_movement(system_name, scan_date, item, system_dict, update_reason))
            else:
              data = add_data(data, system_name, scan_date, item, system_dict)
        session.commit()
      df = pd.DataFrame(data, columns=['system','scan_date','last_seen','galX','galY','name','typeName','entityID','entityType','hull','shield','ionic','underConstruction','sharingSensors','sysX','sysY','travelDirection','ownerName','iffStatus','image'])
      df.to_sql(name=system_name, con=engine, if_exists='append')
      try:
        logOutput += f"- Checking for Entities that have exited the system since the last scan.<br/>"
        update_reason = "Left System"
        for row in session.execute(text(f"SELECT * FROM '{system_name}' WHERE last_seen LIKE '%{compareScan}%'")):
          movement.append(add_exit_movement(row, update_reason))
          logOutput += f"--> Ship Named: {row[6]} (ID: {row[8]}, Owner: {row[18]}) left the system.<br/>"
      except:
        logOutput += f"-- No Movement within {system_name} detected.<br/>"
      logOutput += f"### Finished processing {file} ###<br/>"
      session.execute(text(f"INSERT INTO 'Processed Files' (file_name, scan_date, system) VALUES ('{file}', '{scan_date}', '{system_name}')"))
      session.commit()
      enter_system_movement(logOutput, movement, system_name)
  engine.dispose()
  return logOutput

def lookup_entity(entityID,entityName):
  with engine.connect() as conn:
    resultsDF = pd.DataFrame()
    tables = inspect(engine).get_table_names()
    for table in tables:
      try:
        if entityID != "":
          results = pd.read_sql(f"SELECT entityID, name, typeName, ownerName, last_seen, system FROM '{table}' WHERE entityID == '{entityID}'", conn)
          if not results.empty:
            resultsDF = pd.concat([results,resultsDF])
        else: 
          results = pd.read_sql(f"SELECT entityID, name, typeName, ownerName, last_seen, system FROM '{table}' WHERE name LIKE '%{entityName}%'", conn)
          if not results.empty:
            resultsDF = pd.concat([results,resultsDF])
      except:
        pass
  try:    
    resultsDF = resultsDF.sort_values(by=['entityID', 'name', 'last_seen'])
  except:
    resultsDF = pd.DataFrame({'entity': [f"Entity Not Found in search of {tables}"]})
  return resultsDF

def system_report(systemName):
  with engine.connect() as conn:
    resultsDF = pd.DataFrame()
    tables = inspect(engine).get_table_names()
    newestScan = pd.read_sql(f"SELECT system, scan_date FROM 'Processed Files' WHERE system LIKE '%{systemName}%'", conn)
    newestScan = newestScan.sort_values(by=['scan_date'], ascending=False, ignore_index=True).head(1)
    try:
      results = pd.read_sql(f"SELECT entityID, name, typeName, ownerName, last_seen FROM '{newestScan.system.values[0]}' WHERE last_seen LIKE '%{newestScan.scan_date.values[0]}%'", conn)
      if not results.empty:
        resultsDF = pd.concat([results,resultsDF])
    except:
      print("Exception found")
      pass
  try:    
    resultsDF = resultsDF.sort_values(by=['entityID', 'name', 'last_seen'])
  except:
    resultsDF = pd.DataFrame({f"System Data for {systemName}": [f"{systemName} Not Found in search of {tables}"]})
  return resultsDF

def system_movement(systemName):
  with auxEngine.connect() as conn:
    resultsDF = pd.DataFrame()
    tables = inspect(engine).get_table_names()
    for table in tables:
      try:
        newestScan = pd.read_sql(f"SELECT system FROM '{table}' WHERE system LIKE '%{systemName}%'", conn)
        resultsDF = pd.read_sql(f"SELECT last_seen, update_reason, entityID, name, typeName, ownerName FROM '{newestScan.system.values[0]}'", conn)
      except:
        pass
  try:
    resultsDF = resultsDF.sort_values(by=['last_seen','update_reason','name'], ascending=False, ignore_index=True)
  except:
    resultsDF = pd.DataFrame({f"System Data for {systemName}": [f"{systemName} Not Found in search of {tables}"]})
  return resultsDF