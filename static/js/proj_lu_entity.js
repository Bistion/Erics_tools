var entitysByClass = {
  ship: ["","Super Capitals","Capital Ships","Frigates","Corvettes","Heavy Freighters","Light Freighters","Gunboats","Fighters","Satellites","Cargo Containers"],
  vehicle: ["","Ground Vehicles","Speeders","Barges","Boats and Submarines"],
  droid: ["","Astromech","Military","Protocol","medical","Labour","Security","Power"],
  item: ["","Survival","Tools","Storage","Clothing","Armour","Computers","Medical Items","Drugs","Cybernetics","Trophy","Lightsaber Parts"],
  weapon: ["","Projectile","Heavy Projectile","Non-Projectile"],
  station: ["","Space Stations"],
  facility: ["","1x1","1x3","1x5","1x10","1x19","3x3","3x5","4x7","4x8","5x5","6x6","7x7","8x8","9x9","10x10","20x20"]
}

  function setClass(value) {
    if (value.length == 0) document.getElementById("entityClass").innerHTML = "<option></option>";
    else {
      var classOptions = "";
      for (classId in entitysByClass[value]) {
        classOptions += "<option>" + entitysByClass[value][classId] + "</option>";
      }
      document.getElementById("entityClass").innerHTML = classOptions;
    }
  }

// var entityList = JSON.parse(document.getElementById("entityDiv"))
  function setEntity(value) {
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

  function setStartSystem(value) {
    var systemJson = JSON.parse(systemList)
    if (value.length == 0) document.getElementById("systemStartName").innerHTML = "<option></option>";
    else {
      var systemOptions = "<option></option>";
      for (var i = 0; i < systemJson.length; i++) {
        if (systemJson[i].sector_name == value) {
          systemOptions += "<option>" + systemJson[i].system_name + "</option>";
        }
      }
      document.getElementById("systemStartName").innerHTML = systemOptions;
    }
  }
  function setEndSystem(value) {
    var systemJson = JSON.parse(systemList)
    if (value.length == 0) document.getElementById("systemEndName").innerHTML = "<option></option>";
    else {
      var systemOptions = "<option></option>";
      for (var i = 0; i < systemJson.length; i++) {
        if (systemJson[i].sector_name == value) {
          systemOptions += "<option>" + systemJson[i].system_name + "</option>";
        }
      }
      document.getElementById("systemEndName").innerHTML = systemOptions;
    }
  }