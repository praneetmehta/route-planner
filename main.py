import numpy as np
import math
from util import Coord, Distance, Node, Euclidean
import os
import json
import pickle
from Astar import Astar
import re
from fuzzywuzzy import fuzz
import time

d = Distance()
e = Euclidean()
astar = Astar()
nodes = []
APIs = None
with open('API', 'r') as file:
	APIs = file.read().split('\n')
	print('{} APIs successfully read'.format(len(APIs)))
child_count = 7
places = []

def generateGraph(outfile, cc = child_count):
	global nodes, places

	d.setAPI(APIs[0])
	usedApi = APIs.pop(0)
	APIs.append(usedApi)
	outfile = open(outfile, 'r')
	outdata = outfile.read().split('\n')
	outdata = [s.split(';') for s in outdata]
	outfile.close()
	places = [n[0].lower() for n in outdata]
	nodes = [Node(n[0], n[1], n[2]) for n in outdata]
	for i, ni in enumerate(nodes):
		childs = []
		for j, nj in enumerate(nodes):
			if(i != j):
				euclid_distance = e.eucl(ni.lat, ni.lon, nj.lat, nj.lon)
				if euclid_distance > float(0) and euclid_distance < float(10):
					childs.append([euclid_distance, nj])
		childs = sorted(childs, key = lambda k: k[0], reverse = False)
		childs = childs[:cc]
		for child in childs:
			ni.addChild(child[1], child[0], 0, 0)
			child[1].addChild(ni, child[0], 0, 0)

def fetchDetails(nodes, dist_duration):
	global APIs, child_count
	for _, node in enumerate(nodes):
		print("{0:.2%}, {1} {2}".format(_/len(nodes), node.name, len(node.child)))
		chi = node.getChildIds()
		for c in chi:
			for attempt in range(len(APIs)):
				try:
					if node.child[c]['dist'] == 0:
						C = Node.getNodeById(c)
						d.setCoord(node.lat, node.lon, C.lat, C.lon)
						dist, duration = d.fetch()
						dist_duration.append([node.id, c, dist, duration])
						print('->',C.id,  C.name, node.child[c]['edist'], dist, duration)
				except:
					print('Error in {}, Switching Api Keys'.format(c))
					time.sleep(2)
					d.setAPI(APIs[0])
					usedApi = APIs.pop(0)
					APIs.append(usedApi)
					continue
				break
	return dist_duration


def checkForUpdates():
	dataUpdate = ''
	if os.path.isfile('toAdd.txt'):
		with open('toAdd.txt', 'r') as file:
			dataUpdate = file.read()
		if len(dataUpdate.split('\n')) >= 1 and dataUpdate.split('\n')[0] != 'False':
			with open('toAdd.txt', 'w') as file:
				file.write('False\n'+dataUpdate)
			with open('newCoords.txt', 'a') as file:
				for line in dataUpdate.strip('\n').split('\n'):
					file.write('\n'+line)
			return True, len(dataUpdate.strip('\n').split('\n'))
	return False, 0


def updateGraph(dist_duration):
	global nodes
	for pair in dist_duration:
		parent_id, child_id, dist, duration = pair
		parent_node = Node.getNodeById(parent_id)
		dist = float(re.sub('[^0-9.]', '', dist).strip())
		duration = float(re.sub('[^0-9.]', '', duration).strip())
		parent_node.update(child_id, dist, duration)


def printGraph():
	global nodes
	for node in nodes:
		print(node.id, node.name, len(node.child))
		chi = node.getChildIds()
		for c in chi:
			C = Node.getNodeById(c)
			print('->',C.id,  C.name, node.child[c]['edist'], node.child[c]['dist'], node.child[c]['duration'])


def matchPlace(text):
	text = text.lower()
	max_ratio = 0
	found_string = None
	for string in places:
		ratio = fuzz.ratio(string, text)
		if ratio > max_ratio:
			found_string = string
			max_ratio = ratio
	return found_string

if __name__ == "__main__":
	if not os.path.exists('newCoords.txt'):
		open('newCoords.txt', 'w').close()
		c = Coord('localities.txt', 'newCoords.txt')
		c.getCoord()
	else:
		print('Coordinate File Exists')

	updateStatus, toUpdate = checkForUpdates()
	print(toUpdate, updateStatus)
	if updateStatus:
		generateGraph('newCoords.txt', cc=15)
	else:
		generateGraph('newCoords.txt')
	dist_duration = []

	if not os.path.isfile('dist_duration_large.pkl'):
		dist_duration = fetchDetails(nodes, dist_duration)
		with open('dist_duration_large.pkl', 'wb') as file:
			pickle.dump(dist_duration, file)
		print('All details fetched successfully')
	elif updateStatus:
		with open('dist_duration_large.pkl', 'rb') as file:
			dist_duration = pickle.load(file)
		nodesToUpdate = [node for node in nodes[len(nodes)-toUpdate:]]
		dist_duration = fetchDetails(nodesToUpdate, dist_duration)
		with open('dist_duration_large.pkl', 'wb') as file:
			pickle.dump(dist_duration, file)
		print('All new nodes Updated successfully')

	with open('dist_duration_large.pkl', 'rb') as file:
		dist_duration = pickle.load(file)
	print('All details updated successfully')

	updateGraph(dist_duration)

	src = Node.getIdByName(matchPlace('Bits Pialni'))
	dest = Node.getIdByName(matchPlace('Rajiv Gandhi Airport'))
	astar.dest = dest
	astar.src = src
	astar.findRoute()
	astar.backtrack()
	astar.drawMap()

