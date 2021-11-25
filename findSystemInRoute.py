# Find Current System in route
def findSystemInRoute(navRouteData, ax, currentSystem, scoop, nonScoop, scoopMapping):
	# Initialize Variables
	xStarPos = []
	yStarPos = []
	zStarPos = []
	starClass = []
	starSystem = []
	currentSystemFoundInRoute = False
	currentSystemStartIndex = 0
	routeLength = 0
	visibleRouteLength = 0

	if len(navRouteData['Route']) > 1:
		for route in navRouteData['Route']:
			if currentSystemFoundInRoute == False:
				if route['StarSystem'] == currentSystem:
					currentSystemFoundInRoute = True
				else:
					currentSystemStartIndex += 1
				if route['StarSystem'] == navRouteData['Route'][-1]['StarSystem']:
					break
			if currentSystemFoundInRoute == True and visibleRouteLength < 10:
				visibleRouteLength += 1
				ax.scatter((route['StarPos'][0]), (route['StarPos'][1]), (route['StarPos'][2]), c=scoopMapping[route['StarClass']], s=100, marker=('$' + route['StarClass'] + '$'))
				xStarPos.append(route['StarPos'][0])
				yStarPos.append(route['StarPos'][1])
				zStarPos.append(route['StarPos'][2])
				starClass.append(route['StarClass'])
				starSystem.append(route['StarSystem'])
				ax.plot(xStarPos,yStarPos,zStarPos, color='0.4', zorder=1, linestyle='solid')
				routeLength = visibleRouteLength
			elif currentSystemFoundInRoute == True and routeLength == 10:
				xStarPos.append(route['StarPos'][0])
				yStarPos.append(route['StarPos'][1])
				zStarPos.append(route['StarPos'][2])
				starClass.append(route['StarClass'])
				starSystem.append(route['StarSystem'])
				ax.plot(xStarPos,yStarPos,zStarPos, color='0.4', zorder=1, linestyle='dashed')
				routeLength += 1
			elif currentSystemFoundInRoute == True and routeLength == 11:
				xStarPos.append(navRouteData['Route'][-1]['StarPos'][0])
				yStarPos.append(navRouteData['Route'][-1]['StarPos'][1])
				zStarPos.append(navRouteData['Route'][-1]['StarPos'][2])
				starClass.append(navRouteData['Route'][-1]['StarClass'])
				starSystem.append(navRouteData['Route'][-1]['StarSystem'])
				routeLength += 1
			elif currentSystemFoundInRoute == True and routeLength > 11:
				routeLength += 1
	return xStarPos, yStarPos, zStarPos, starClass, starSystem, routeLength, visibleRouteLength