import heapq
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
from shapely.geometry import Point, box
from shapely import GeometryCollection, LineString, MultiPoint, wkt
from shapely.geometry.polygon import Polygon
import pandas as pd
import os, xmltodict, math, requests
from models.base import Base

engine = create_engine(f"sqlite:///swc_info.db", echo=False)

class Node:
  def __init__(self, position, cost):
    self.position = position
    self.cost = cost
    self.parent = None  # Add a parent attribute to track the path

  def __lt__(self, other):
    return self.cost < other.cost

def astar_search(box, start, goal, hs, piloting):
  open_set = []
  closed_set = set()
  start_node = Node(start, 0)
  heapq.heappush(open_set, start_node)
  while open_set:
    current_node = heapq.heappop(open_set)

    if current_node.position == goal:
      # Path found, reconstruct and return it
      path = []
      while current_node:
        path.insert(0, current_node.position)
        current_node = current_node.parent
      return path

    closed_set.add(current_node.position)
    hl_coords = get_hyperlanes(current_node.position)
    for neighbor in hl_coords:
      sysName = neighbor.split(",")[2]
      endX, endY = int(neighbor.split(",")[0]), int(neighbor.split(",")[1])
      point = Point(endX,endY)
      if (box.contains(point)) or (sysName == goal):
        if sysName not in closed_set:
          curX, curY = calc_points(current_node.position)
          hl_val = float(neighbor.split(",")[3])
          
          total = max(abs(curX - endX), abs(curY - endY))
          cost = current_node.cost + calculate_eta(total,hs,piloting,hl_val)
          # heuristic_val = hl_val
          new_node = Node(sysName, cost)
          new_node.parent = current_node

          # Check if the neighbor is already in the open set with a lower cost
          existing_node = next((node for node in open_set if node.position == sysName), None)
          if existing_node and existing_node.cost <= cost:
            continue

          heapq.heappush(open_set, new_node)
  return None

def calc_points(system):
  system = system.replace("'","''")
  with engine.connect() as conn:
    results = pd.read_sql(f"SELECT * FROM 'system_info' WHERE system_name == '{system}'", conn)
  foundX = results.x_coord.loc[results.index[0]]
  foundY = results.y_coord.loc[results.index[0]]
  return foundX, foundY

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
    hl = 1
  if hl > 100:
    hl = 0.999
  # hl = 1 - (hl / 100)
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

def start_pathing(startSystem, endSystem, hs, piloting):
  hs, piloting = int(hs), int(piloting)
  initialX, initialY = calc_points(startSystem) 
  endX, endY = calc_points(endSystem)
  full_total = max(abs(initialX - endX), abs(initialY - endY))
  graph1 = LineString([(initialX,initialY),(endX,endY)]).offset_curve(30)
  graph2 = LineString([(initialX,initialY),(endX,endY)]).offset_curve(-30)
  start_node = startSystem
  goal_node = endSystem
  box = Polygon([graph1.coords[0],graph1.coords[1],graph2.coords[0],graph2.coords[1]])
  path = astar_search(box, start_node, goal_node, hs, piloting)
  if path:
    print("Path found:", path)
    i = 1
    leg_eta, path_eta, path_output, prettyPath = "",[],[], f"{startSystem}"
    for sys in path:
      if sys != endSystem:
        with engine.connect() as conn:
          clean_sys = sys.replace("'","''")
          sysPath = path[i].replace("'","''")
          startResults = pd.read_sql(f"SELECT * FROM 'system_info' WHERE system_name == '{clean_sys}'", conn)
          endResults = pd.read_sql(f"SELECT * FROM 'system_info' WHERE system_name == '{sysPath}'", conn)
        initialX = startResults.x_coord.loc[startResults.index[0]]
        initialY = startResults.y_coord.loc[startResults.index[0]]
        endX = endResults.x_coord.loc[endResults.index[0]]
        endY = endResults.y_coord.loc[endResults.index[0]]
        total = max(abs(initialX - endX), abs(initialY - endY))
        hl_coords = get_hyperlanes(sys)
        for lane in hl_coords:
          sysName = lane.split(",")[2]
          if path[i] == sysName:
            hl_val = float(lane.split(",")[3])
            leg_eta = calculate_eta(total,hs,piloting,hl_val)
            path_eta.append(leg_eta)
            prettyPath += f" -> {path[i]}"
            path_output.append(f"{sys} to {path[i]}: {display_eta(leg_eta)}")
        i += 1
    seconds = 0
    for eta in path_eta:
      seconds += eta
    full_eta = display_eta(seconds)
    path_output.append(f"Total: {full_eta}")
    direct_eta = calculate_eta(full_total,hs,piloting,1)
    print(path_output)
    print(direct_eta)
    direct_eta = f"Direct Path: {display_eta(direct_eta)}"
    return prettyPath, direct_eta, path_output
  else:
    path ="Hit a dead end: No path found"
    direct_eta = calculate_eta(full_total,hs,piloting,1)
    direct_eta = f"Direct Path: {display_eta(direct_eta)}"
    path_output = ""
    return path, direct_eta, path_output