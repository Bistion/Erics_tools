
  function setSector(value) {
    if (value.length == 0) document.getElementById("entityClass").innerHTML = "<option></option>";
    else {
      var classOptions = "";
      for (classId in entitysByClass[value]) {
        classOptions += "<option>" + entitysByClass[value][classId] + "</option>";
      }
      document.getElementById("entityClass").innerHTML = classOptions;
    }
  }

  function setSystem(value) {
    var entityJson = JSON.parse(entityList)
    if (value.length == 0) document.getElementById("entityName").innerHTML = "<option></option>";
    else {
      var entityOptions = "<option></option>";
      for (var i = 0; i < entityJson.length; i++) {
        if (entityJson[i].class == value) {
          entityOptions += "<option>" + entityJson[i].name + "</option>";
        }
      }
      document.getElementById("entityName").innerHTML = entityOptions;
    }
  }