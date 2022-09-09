import dijkstra
import datetime
import json
from util import *

def readCache():
  try:
    with open('.cache') as f:
      routeCache = json.load(f)
  except FileNotFoundError:
      routeCache = {}
#      printVerbose("Route cache not found",verbose)
  except json.decoder.JSONDecodeError:
      routeCache = {}
#      printVerbose("Route cache empty",verbose)
  return routeCache
def writeCache(cache):
  print(cache)
  with open('.cache',"w") as f:
    routeCache = json.dump(cache, f)
  return routeCache

def calculateRoute(sX,sY,tX,tY,verbose,world):
  printVerbose("Calculating route from "+str(sX)+":"+str(sY)+" to "+str(tX)+":"+str(tY),verbose)
  cache = readCache()
  routeName = sX+":"+sY+";"+tX+":"+tY
  if not routeName in cache:
    printVerbose("Route not found in cache",verbose)
    (orderlist,operation_duration, operation, shortestpath) = dijkstra.dijkstra(int(sX),int(sY),int(tX),int(tY),0,world)
    cache[routeName] = {}
    cache[routeName]["orderlist"] = orderlist
    cache[routeName]["operation_duration"] = str(operation_duration)
    writeCache(cache)
  else:
    printVerbose("Route found in cache",verbose)
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
      printVerbose("Adding travel commands",verbose)
      addTravel(order[0],order[1])
