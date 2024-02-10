import EgCli.dijkstra
import datetime
import json
from EgCli.util import *

def readCache():
  try:
    with open('.cache') as f:
      routeCache = json.load(f)
  except FileNotFoundError:
      routeCache = {}
#      print_verbose("Route cache not found")
  except json.decoder.JSONDecodeError:
      routeCache = {}
#      print_verbose("Route cache empty")
  return routeCache
def writeCache(cache):
  print(cache)
  with open('.cache',"w") as f:
    routeCache = json.dump(cache, f)
  return routeCache

def calculateRoute(sX,sY,tX,tY,verbose,world):
  print_verbose("Calculating route from "+str(sX)+":"+str(sY)+" to "+str(tX)+":"+str(tY))
  cache = readCache()
  routeName = sX+":"+sY+";"+tX+":"+tY
  if not routeName in cache:
    print_verbose("Route not found in cache")
    (orderlist,operation_duration, operation, shortestpath) = dijkstra.dijkstra(int(sX),int(sY),int(tX),int(tY),0,world)
    cache[routeName] = {}
    cache[routeName]["orderlist"] = orderlist
    cache[routeName]["operation_duration"] = str(operation_duration)
    writeCache(cache)
  else:
    print_verbose("Route found in cache")
    orderlist = cache[routeName]['orderlist']
    operation_duration = cache[routeName]['operation_duration']
  return orderlist,operation_duration

def addTravel(tX,tY):
  data = {
    'page': 'group_travel',
    'action': 'group_task_travel',
    'selection': 0,
    'town_id':3,
    'token': getToken('group_travel'),
    'freex': tX,
    'freey': tY
  }
  response = requests.request('POST','https://evergore.de/zyrthania?page=group_travel',headers=HDRS,data=data)

def travel(source,target,verbose,add,list,create,world):
  sX,sY = splitCoord(source)
  tX,tY = splitCoord(target)
  orderlist,duration = calculateRoute(sX,sY,tX,tY,verbose,world)
  date = datetime.datetime.now()
  sumTime = sum(o[2] for o in orderlist)
  if list:
    print("Gesamte Dauer: "+str(sumTime))
    for order in orderlist:
      print(order)
      try:
        print(str(order[0])+":"+str(order[1])+" "+str(lastTime + (datetime.timedelta(minutes=order[2]) )))
      except UnboundLocalError:
        print(str(order[0])+":"+str(order[1])+" "+str(date + datetime.timedelta(minutes=order[2])))
      lastOrder = order
      lastTime = date + datetime.timedelta(minutes=order[2])
  if add:
    for order in orderlist:
      print_verbose("Adding travel commands")
      addTravel(order[0],order[1])
