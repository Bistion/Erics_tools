from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
import pandas as pd
import os, xmltodict
from dotenv import load_dotenv
from models.base import Model

# load_dotenv()
# TURSO_DATABASE_URL= os.getenv("TURSO_DATABASE_URL")
# TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
# dbUrl = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"
# engine = create_engine(dbUrl, connect_args={'check_same_thread': False}, echo=False)
engine = create_engine(f"sqlite:///var/data/System_Scans.db", echo=False)

def enter_scan():
  Model.metadata.create_all(engine)
  dir_path = os.path.abspath(os.path.dirname(__file__))
  logOutput = ""
  for root, dirs, files in os.walk(f"{dir_path}/uploads"):
    for file in files:
      with open(f"{dir_path}/uploads/{file}", 'r', encoding='ISO-8859-1') as f:
        system_dict = xmltodict.parse(f.read())
        system = system_dict['rss']['channel']['title'].split('Scan of ')
        system_name = system[1]
        scan_date = system_dict['rss']['channel']['lastBuildDate']
        logOutput += "<h3>------------------</h3><br/>"

      with Session(engine) as session:
        # Continue to next file if coords in the system_name
        if "coords" in system_name:
          logOutput += f"<h3>### File Processing Error!!!! ###</h3><br/>Send the following file to Eric for troubleshooting.<br/>- {file}<br/>"
          os.remove(f"{dir_path}/uploads/{file}")
          continue 
        data = []
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
          os.remove(f"{dir_path}/uploads/{file}")
          continue
        else:
          with engine.connect() as conn:
            newestScan = pd.read_sql(f"SELECT system, scan_date FROM 'Processed Files' WHERE system == '{system_name}'", conn)
            newestScan = newestScan.sort_values(by=['scan_date'], ascending=False, ignore_index=True).head(1)
            try:
              compareScan = newestScan['scan_date'].loc[newestScan.index[0]]
              if scan_date > compareScan:
                logOutput += f"Scan date of {scan_date} is newer than last processed scan date of {compareScan}.  Continuing file processing.<br/>"
              else:
                logOutput += f"File Scan date of {scan_date} is older than the newest scan data from {compareScan}.---->Skipping.<br/>"
                os.remove(f"{dir_path}/uploads/{file}")
                continue
            except:
              pass
          os.remove(f"{dir_path}/uploads/{file}")
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
              continue 
            if not first_search:
              second_search = session.execute(text(f"SELECT name FROM '{system_name}' WHERE entityID == '{item['entityID']}'")).all()
              if second_search:
                logOutput += f"* Entity with an ID of {item['entityID']} already entered as {second_search}, but is now reporting a different name.<br/> --> Updating name to be {item['name']}<br/>"
                session.execute(text(f"UPDATE '{system_name}' SET last_seen='{scan_date}', name='{item['name']}' WHERE entityID == '{item['entityID']}'"))
                session.execute(text(f"INSERT INTO 'Entity Changes' (entityID, name, last_seen, typeName, system) VALUES ('{item['entityID']}', '{item['name']}', '{scan_date}', '{item['typeName']}', '{system[1]}')"))
                session.commit()
                continue
              else:
                logOutput += f"- New entity found.  Adding {item['name']}(ID#: {item['entityID']}) to {system_name}<br/>"
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
          session.commit()
      df = pd.DataFrame(data, columns=['system','scan_date','last_seen','galX','galY','name','typeName','entityID','entityType','hull','shield','ionix','underConstruction','sharingSensors','sysX','sysY','travelDirection','ownerName','iffStatus','image'])
      df.to_sql(name=system_name, con=engine, if_exists='append')
      logOutput += f"### Finished processing {file} ###<br/>"
      session.execute(text(f"INSERT INTO 'Processed Files' (file_name, scan_date, system) VALUES ('{file}', '{scan_date}', '{system_name}')"))
      session.commit()
  engine.dispose()
  return logOutput

def lookup_entity(entityID,entityName):
  #engine = create_engine(f"sqlite:///New_System_Scans.db", echo=False)
  with engine.connect() as conn:
    resultsDF = pd.DataFrame()
    tables = inspect(engine).get_table_names()
    for table in tables:
      try:
        if entityID != "":
          results = pd.read_sql(f"SELECT entityID, name, typeName, last_seen, system FROM '{table}' WHERE entityID == '{entityID}'", conn)
          if not results.empty:
            resultsDF = pd.concat([results,resultsDF])
        else: 
          results = pd.read_sql(f"SELECT entityID, name, typeName, last_seen, system FROM '{table}' WHERE name LIKE '%{entityName}%'", conn)
          if not results.empty:
            resultsDF = pd.concat([results,resultsDF])
      except:
        pass
  resultsDF = resultsDF.sort_values(by=['entityID', 'name', 'last_seen'])
  return resultsDF




          