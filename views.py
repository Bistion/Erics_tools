from flask import Blueprint, render_template, request, redirect
import os, time, json
from werkzeug.utils import secure_filename
import pandas as pd
from dbSystem import *
from dbProject import *
from hyper_calc import *

views = Blueprint(__name__, "views")

def color_cells(s):
  color = {"Entered System": "green", "Left System": "red"}
  return ['background-color: ' + color[s["update_reason"]] for s_ in s]

@views.route("/")
def home():
  return render_template("home.html", titleVal="Home", class1='class=position-relative, style="padding: 100px"',class2="d-none")

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
    print(f"From: {startSector}/{startSystem}")
    print(f"To: {endSector}/{endSystem}")
    print(f"Using: Hyperspeed: {hyperspeed} / PilotSkill: {pilotSkill}")
    path, direct_eta, path_output = start_pathing(startSystem, endSystem, hyperspeed, pilotSkill)
    sectorList = get_sector_list()
    systemList = get_system_list()
    end = time.time()
    total = end - start
    print(f"Time to run check: {total}")
    pathHead = f"From {startSector}/{startSystem} to {endSector}/{endSystem} using hyper {hyperspeed} and piloting {pilotSkill}"
    total = f"Total time in seconds to calculate quickest path: {total}"
    return render_template('hyper_calculator.html', sectorJson=sectorList, systemJson=systemList, pathHead=pathHead, path=path, direct_eta=direct_eta, path_output=path_output, total=total,hideMe="container")
  else:
    sectorList = get_sector_list()
    systemList = get_system_list()
    return render_template('hyper_calculator.html', sectorJson=sectorList, systemJson=systemList, hideMe="d-none")
  
@views.route("/about")
def about():
  return render_template("home.html", titleVal="About",class1="d-none",class2="position-relative")