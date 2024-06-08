from flask import Blueprint, render_template, request, redirect
import os, time, json
from werkzeug.utils import secure_filename
import pandas as pd
from dbSystem import *
from dbProject import *

views = Blueprint(__name__, "views")

def color_cells(s):
  color = {"Entered System": "green", "Left System": "red"}
  return ['background-color: ' + color[s["update_reason"]] for s_ in s]

@views.route("/")
def home():
  return render_template("home.html")

@views.route("/new-scan")
def new_scan():
  return render_template("new_scan.html")

@views.route("/upload", methods=['GET','POST'])
def upload():
  dir_path = os.path.dirname(os.path.realpath(__file__))
  if request.method == 'POST':
    try:
      os.remove("./templates/logOutput.html")
    except:
      pass
    files = request.files.getlist('files')
    for file in files:
      fn = secure_filename(file.filename)
      # file.save(os.path.join('/var/data/uploads', fn))
      file.save(os.path.join('./uploads', fn))
    logOutput = enter_scan()
    with open ("./templates/logOutput.html", 'w', encoding="utf-8") as lo:
      lo.write(logOutput)
    return render_template('upload_log.html')
  else:
    return redirect("/new-scan")

@views.route("/entity-lookup", methods=['GET','POST'])
def entity_lookup():
  if request.method == 'POST':
    entityID = request.form.get('entityID')
    entityName = request.form.get('entityName')
    results = lookup_entity(entityID,entityName)
    value = pd.DataFrame(results)
    return render_template('entity_lookup_results.html', tables=[value.to_html(classes='table-style', index=False)], titles=value.columns.values, value=f"{entityID}{entityName}")
  else:  
    return render_template("entity_lookup.html")
  
@views.route("/system-report", methods=['GET','POST'])
def system_report_view():
  if request.method == 'POST':
    system = request.form.get('system')
    results = system_report(system)
    value = pd.DataFrame(results)
    return render_template('entity_lookup_results.html', tables=[value.to_html(classes='table-style', index=False)], titles=value.columns.values, value=system)
  else:  
    return render_template("system_report.html")
  
@views.route("/system-movement", methods=['GET','POST'])
def system_movement_view():
  if request.method == 'POST':
    system = request.form.get('system')
    results = system_movement(system)
    value = pd.DataFrame(results)
    # value = value.style.apply(color_cells, axis=1)
    return render_template('entity_lookup_results.html', tables=[value.to_html(classes='table-style', index=False)], titles=value.columns.values, value=system)
  else:  
    return render_template("movement_report.html")
  
@views.route("/estimate-project", methods=['GET','POST'])
def project_estimate_view():
  if request.method == 'POST':
    entityType = request.form.get('entityType')
    entityClass = request.form.get('entityClass')
    entityName = request.form.get('entityName')
    entityQty = request.form.get('entityQty')
    logOutput = project_estimate(entityType,entityClass,entityName,entityQty)
    with open ("./templates/logOutput.html", 'w', encoding="utf-8") as lo:
      lo.write(logOutput)
    return render_template('upload_log.html')
  else:
    entityList = get_entity_list()
    return render_template('proj_lu_entity.html', entityJson=entityList)
  
@views.route("/hyperspace", methods=['GET','POST'])
def hyperspace_calculator():
  if request.method == 'POST':
    start = time.time()
    startSector = request.form.get('startSector')
    startSystem = request.form.get('startSystem')
    endSector = request.form.get('endSector')
    endSystem = request.form.get('endSystem')
    pilotSkill = request.form.get('pilotSkill')
    hyperspeed = request.form.get('hyperspeed')
    
    hyperlane = 0
    print(f"startSector: {startSector}")
    print(f"startSystem: {startSystem}")
    print(f"endSector: {endSector}")
    print(f"endSystem: {endSystem}")
    print(f"hyperspeed: {hyperspeed}")
    print(f"pilotSkill: {pilotSkill}")
    url = 'https://h2fptpbb7b5jcuzit7dcus7zli0svjrn.lambda-url.us-east-2.on.aws/'
    headers = {'Content-type': 'application/json'}
    data = '{\"startSystem\":"'+startSystem+'",\"endSystem\":"'+endSystem+'",\"hs\":"'+hyperspeed+'",\"piloting\":"'+pilotSkill+'"}'
    
    results = requests.post(url, data=data, headers=headers)
    print(f"Lambda results: {results}")
    value = pd.DataFrame(results)
    # value = value.drop(['index'], axis=1)
    # properties = {"border": "2px solid gray", "color": "white", "font-size": "16px","justify": "center", "index": "False"}
    # value = value.style.set_properties(**properties)
    sectorList = get_sector_list()
    systemList = get_system_list()
    end = time.time()
    total = end - start
    print(f"Time to run check: {total}")
    path = f"From {startSector}/{startSystem} to {endSector}/{endSystem} using hyper {hyperspeed} and piloting {pilotSkill}"
    total = f"Total Time in Seconds: {total}"
    return render_template('hyper_calculator.html', sectorJson=sectorList, systemJson=systemList, tables=[value.to_html(classes="table table-dark table-hover",justify="center", index=False)], titles=value.columns.values, path=path, total=total)

  else:
    sectorList = get_sector_list()
    systemList = get_system_list()
    return render_template('hyper_calculator.html', sectorJson=sectorList, systemJson=systemList)