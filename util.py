from geopy.geocoders import Nominatim
import requests
import math
import json
import re
import os

class Distance(object):
	
	def __init__(self, ax=0, ay=0, bx=0, by=0):
		self.src_lat = ax
		self.src_long = ay
		self.dest_lat = bx
		self.dest_long = by
		self.URL = None
		self.data = None

	def setCoord(self, ax=0, ay=0, bx=0, by=0):
		self.__init__(ax, ay, bx, by)
		self.generateURL()

	def setAPI(self, key):
		self.API_KEY = key

	def generateURL(self):
		self.URL = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&" + \
					"origins={0},{1}&".format(self.src_lat, self.src_long) + \
					"destinations={0},{1}&key={2}".format(self.dest_lat, self.dest_long, self.API_KEY)
		# print(self.URL)

	def fetch(self):
		self.data = requests.get(self.URL).text
		distance = json.loads(self.data)['rows'][0]['elements'][0]['distance']['text']
		duration = json.loads(self.data)['rows'][0]['elements'][0]['duration']['text']
		return distance, duration

class Euclidean(object):
	def __init__(self, ax=0, ay=0, bx=0, by=0):
		ax = math.radians(float(ax))
		ay = math.radians(float(ay))
		bx = math.radians(float(bx))
		by = math.radians(float(by))
		self.x1 = 6731*math.cos(ax)*math.cos(ay)
		self.y1 = 6731*math.cos(ax)*math.sin(ay)
		self.z1 = 6731*math.sin(ax)
		self.x2 = 6731*math.cos(bx)*math.cos(by)
		self.y2 = 6731*math.cos(bx)*math.sin(by)
		self.z2 = 6731*math.sin(bx)

	def eucl(self, ax, ay, bx, by):
		self.__init__(ax, ay, bx, by)
		return math.sqrt(math.pow(self.x1-self.x2, 2) + math.pow(self.y1-self.y2, 2) + math.pow(self.z1-self.z2, 2))

class Coord(object):
	
	def __init__(self, INFILE, OUTFILE):
		self.nom = Nominatim()
		self.names = None
		self.infile = INFILE
		self.outfile = OUTFILE
		self.getLocNames()

	def getLocNames(self):
		with open(self.infile,'r') as file:
			data = file.read()
		self.names = data.split('\n')
		self.names = [s + ', Hyderabad' for s in self.names]

	def getCoord(self):
		if not os.path.exists(self.outfile):
			open(self.outfile, 'w').close()
		writefile = open(self.outfile,'r+')
		if self.names is not None:
			for i, place in enumerate(self.names):
				try:
					# p = self.nom.geocode(place)
					# writefile.write("{};{};{}\n".format(place, p.latitude, p.longitude))
					URL = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(re.sub(' ', '+', place), 'AIzaSyBAxYsJRe6dnQFrBp4K60Tf3jlOpeIdsxc')
					print("{0:.2%}\t{1}".format(i/len(self.names), place))
					response = requests.get(URL)
					resp_json_payload = response.json()
					obj = resp_json_payload['results'][0]['geometry']['location']
					print(obj)
					lat = obj['lat']
					lon = obj['lng']
					writefile.write("{};{};{}\n".format(re.sub(', Hyderabad', '', place).strip(), lat, lon))
					print('Written ',place)
				except:
					print("Couldn't find ", place)
				
		writefile.close()

class Node(object):

	NodeID = 0
	nodes = {}
	nameID = {}
	def __init__(self, name, lat, lon):
		Node.NodeID += 1
		self._id = Node.NodeID
		self._children = {}
		self.g = math.inf
		self.h = math.inf
		self.f = math.inf
		self._name = name
		self._lat = float(lat)
		self._lon = float(lon)
		self.path = []
		Node.nodes[self._id] = self
		Node.nameID[name.strip().lower()] = self._id
	
	@property
	def lat(self):
		return self._lat

	@property
	def lon(self):
		return self._lon

	@property
	def name(self):
		return self._name

	@property
	def id(self):
		return self._id

	@property
	def child(self):
		return self._children

	def addChild(self, child, eucl_dist, dist, duration):
		if(child.id == self.id):
			print('Cannot add self as a child')
			return
		elif(child.id in self.child.keys()):
			pass
		else:
			self.child[child.id] = {'node':child, 'edist':eucl_dist, 'dist':dist, 'duration':duration}
	
	def isChild(self, child):
		try:
			a = self.child[child.id]
			return True
		except KeyError:
			return False

	def getChildIds(self):
		child_id = [k for k in self.child.keys()]
		return child_id

	def hgf(self, h, g):
		self.g = g
		self.h = h
		self.f = g+h

	def update(self, child_id, dist, durn):
		if child_id in self.child.keys():
			self.child[child_id]['dist'] = dist
			self.child[child_id]['duration'] = durn
			Node.getNodeById(child_id).child[self.id]['dist'] = dist
			Node.getNodeById(child_id).child[self.id]['duration'] = durn

	@classmethod
	def actualDist(cls, src_id, dest_id):
		src_node = Node.nodes[src_id]
		return src_node.child[dest_id]['dist']

	@classmethod
	def getNodeById(cls, _id):
		try:
			return Node.nodes[_id]
		except:
			print('Not found')

	@classmethod
	def getIdByName(cls, name):
		try:
			return Node.nameID[name.lower()]
		except:
			print('Not found')

if __name__ == "__main__":
	e = Euclidean()
	dis = e.eucl(17.4436222,78.3519638,17.4123446, 78.4899194)
	print(dis)