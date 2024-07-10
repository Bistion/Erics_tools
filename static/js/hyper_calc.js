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

var canvas = $("#myCanvas")[0];
var ctx = canvas.getContext("2d");

function draw(pathdisplayJson) {
  setCanvasSize(ctx.canvas);
  ctx.strokeStyle="#FFFFFF";
  ctx.beginPath();
  for (var i = 0; i < pathdisplayJson.length; i++) {
    let x = Math.max(-500, Math.min(500, pathdisplayJson[i].x_coord));
    let y = Math.max(-500, Math.min(500, pathdisplayJson[i].y_coord));
    let newX = 500 + x;
    let newY = 500 - y;
    if (i > 0) {
      ctx.lineTo(newX,newY);
    } else {
      ctx.moveTo(newX,newY);
    }
  }
  ctx.lineWidth = 4;
  ctx.strokeStyle = "yellow";
  ctx.stroke();
}

function setCanvasSize(canvas) {
  var rect = canvas.parentNode.getBoundingClientRect();
  console.log(rect)
  canvas.width = rect.width;
  canvas.height = rect.height;
}

function generatePoints(sectorList,systemList) {
  var secJson = JSON.parse(sectorList);
  var sectorOptions = "<option></option>";
  for (var i = 0; i < secJson.length; i++) {
    sectorOptions += "<option>" + secJson[i].sector_name + "</option>";
  }
  document.getElementById("sectorStartName").innerHTML = sectorOptions;
  document.getElementById("sectorEndName").innerHTML = sectorOptions;
  
  var pathElement = "";
  for (var i = 0; i < pathdisplayJson.length; i++) {
    let x = Math.max(-500, Math.min(500, pathdisplayJson[i].x_coord));
    let y = Math.max(-500, Math.min(500, pathdisplayJson[i].y_coord));
    let newX = 500 + x;
    let newY = 500 - y;
    let sysID = pathdisplayJson[i].system_uid.replace("9:","")
    let sysHref = "https://www.swcombine.com/rules/?Galaxy_Map&systemID=" + sysID
    pathElement = pathElement += '<a class="combatplanet" style="position:absolute;z-index:2;top:' + newY + 'px; left:' + newX + 'px" title="Sector: ' + pathdisplayJson[i].sector_name + '<br>System: '+ pathdisplayJson[i].system_name + ' (' + y + ', ' + x + ')" href="' + sysHref + '" target="_blank"></a>';
  }
  document.getElementById("mapVals").innerHTML = pathElement;
}