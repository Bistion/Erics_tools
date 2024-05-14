from flask import Blueprint, render_template, request, redirect
import os
from werkzeug.utils import secure_filename
import pandas as pd
from database import enter_scan, lookup_entity

views = Blueprint(__name__, "views")

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
    files = request.files.getlist('files')
    for file in files:
      fn = secure_filename(file.filename)
      file.save(os.path.join('./uploads', fn))
    logOutput = enter_scan()
    with open ("templates/logOutput.html", 'w') as lo:
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
    return render_template('entity_lookup_results.html', tables=[value.to_html(classes='table-style', index=False)], titles=value.columns.values)
  else:  
    return render_template("entity_lookup.html")