from fuzzywuzzy import fuzz
import math
from util import Coord
import os

loc_1 = []
loc_2 = []

with open('localities.txt', 'r') as file:
	loc_1 = file.read().split('\n')

with open('localities_2.csv', 'r') as file:
	loc_2 = file.read().split('\n')

newlocation = []
for i in loc_2:
	found = False
	il = i.lower()
	for j in loc_1:
		jl = j.lower()
		if math.sqrt(fuzz.ratio(jl, il)*fuzz.token_set_ratio(jl, il)) > 75:
			print(jl, math.sqrt(fuzz.ratio(jl, il)*fuzz.token_set_ratio(jl, il)))
			found = True
			break
	if found:
		pass
	else:
		newlocation.append(i)
		print(i)
if len(newlocation) != 0:
	newlocations = ('\n').join(newlocation).strip('\n')
	with open('toAdd.txt', 'w') as file:
		file.write(newlocations)
	c = Coord('toAdd.txt', 'toAdd.txt')
	os.remove('toAdd.txt')
	c.getCoord()
	with open('localities.txt', 'a') as file:
		file.write('\n'+newlocations)
else:
	print('Nothing to update')