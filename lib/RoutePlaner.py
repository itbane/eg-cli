import dijkstra
from util import *

def calculateRoute(sX,sY,tX,tY,verbose,world):
  printVerbose("Calculating route from "+str(sX)+":"+str(sY)+" to "+str(tX)+":"+str(tY),verbose)
  (orderlist,operation_duration, operation, shortestpath) = dijkstra.dijkstra(int(sX),int(sY),int(tX),int(tY),0,world)
  return orderlist

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
  orderlist = calculateRoute(sX,sY,tX,tY,verbose,world)
  if list:
    for order in orderlist:
      print(str(order[0])+":"+str(order[1]))
  if add:
    for order in orderlist:
      printVerbose("Adding travel commands",verbose)
      addTravel(order[0],order[1])
