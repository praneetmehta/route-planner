from util import Coord, Distance, Node, Euclidean
import gmplot
import operator
import re

class Astar(object):

	def __init__(self):
		self.openList = {}
		self.closeList = {}
		self._dest_id = None
		self._src_id = None
		self._dest_name = None
		self._src_name = None
		self._dest_node = None
		self._src_node = None
		self.eucl = Euclidean()
		self.time = 0
		self.distance = 0

	@property
	def dest(self):
		return self._dest_id

	@dest.setter
	def dest(self, dest):
		self._dest_id = dest
		self._dest_node = Node.nodes[dest]
		self._dest_name = Node.nodes[dest].name
		print('Destination set to', self._dest_name)

	@property
	def src(self):
		return self._src_id

	@src.setter
	def src(self, src):
		self._src_id = src
		self._src_node = Node.nodes[src]
		self._src_name = Node.nodes[src].name
		self._src_node.hgf(0, 0)
		self.openList[self._src_id] = self._src_node.h
		self._src_node.path.append(self._src_id)
		print('Source set to', self._src_name)

	def heuristic(self, n1_id, n2_id):
		n1 = Node.getNodeById(n1_id)
		n2 = Node.getNodeById(n2_id)
		return self.eucl.eucl(n1.lat, n1.lon, n2.lat, n2.lon)

	def findRoute(self):
		while(len(self.openList.keys()) != 0):
			templist = sorted(self.openList.items(), key = operator.itemgetter(1))
			pid = templist[0][0]
			self.openList.pop(pid)
			parentNode = Node.getNodeById(pid)
			children = parentNode.getChildIds()
			for cid in children:
				c_node = Node.getNodeById(cid)
				if cid == self._dest_id:
					print('found')
					del c_node.path[:]
					for i in parentNode.path:
						c_node.path.append(i)
					c_node.path.append(cid)
					self.openList.clear()
					self.closeList[self._src_id] = self._src_node.f
					break
				h_dist = self.heuristic(cid, self._dest_id)
				g_dist = parentNode.g + Node.actualDist(pid, cid)
				if cid in self.openList.keys():
					if (g_dist < c_node.g):
						c_node.hgf(h_dist, g_dist)
						self.openList[cid] = c_node.f
				elif cid in self.closeList.keys():
					if (g_dist < c_node.g):
						_ = self.closeList.pop(cid)
						c_node.hgf(h_dist, g_dist)
						self.openList[cid] = Node.getNodeById(cid).f
				else:
					c_node.hgf(h_dist, g_dist)
					
					for i in parentNode.path:
						c_node.path.append(i)
					c_node.path.append(cid)
					self.openList[cid] = Node.getNodeById(cid).f
			self.closeList[pid] = Node.getNodeById(pid).f

	def backtrack(self):
		for i in self._dest_node.path:
			print('->',Node.getNodeById(i).name)
		for i in range(len(self._dest_node.path)-1):
			pid = self._dest_node.path[i]
			cid = self._dest_node.path[i+1]
			parent = Node.getNodeById(pid)
			child = Node.getNodeById(cid)
			self.distance += float(parent.child[cid]['dist'])
			self.time += float(parent.child[cid]['duration'])
			print('From {0} to {1} is {2} kms and takes {3} mins'.format(parent.name, child.name, parent.child[cid]['dist'], parent.child[cid]['duration']))
		print('total time', self.time, 'mins')
		print('total distance', self.distance, 'kms')


	def printClosedList(self):
		for i in self.closeList:
			print(i, Node.getNodeById(i).name, Node.getNodeById(i).f, Node.getNodeById(i).g, Node.getNodeById(i).h)

	def drawMap(self):
		lat = []
		lon = []
		loc = []
		for i in self._dest_node.path:
			lat.append(Node.getNodeById(i).lat)
			lon.append(Node.getNodeById(i).lon)
			loc.append(Node.getNodeById(i).name)
		gmap = gmplot.GoogleMapPlotter((lat[0]+lat[-1])/2, (lon[0]+lon[-1])/2, 12)
		gmap.plot(lat, lon, 'cornflowerblue', marker=False, edge_width=7)
		# gmap.scatter(lat, lon, '#4444aa', size=180, marker=False)
		for i in range(len(lat)):
			gmap.marker(lat[i],lon[i],'#FF0000',c=None,title=loc[i])
		# gmap.scatter(lat, lon, '#FF0000', size=60, marker=True, c=None, s=None, title=loc)
		gmap.draw('map.html')
		data = ''
		with open('map.html', 'r') as file:
			data = file.read()
		data = data.replace('\\','/')
		with open('map.html', 'w') as file:
			file.write(data) 