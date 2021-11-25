# Find Next Scoopable Star
def getNextScoopableStar(starClass, scoopMapping, scoop, starSystem):
	scoopableStarFound = False
	scoopableStarIndex = 0
	for nextFuelStar in starClass:
		if scoopMapping[nextFuelStar] == scoop:
			scoopableStarFound = True
			nextScoopableStar = starSystem[scoopableStarIndex]
			if scoopableStarIndex == 0:
				nextScoopableStar = 'Current Star'
			break
		scoopableStarIndex += 1
	if scoopableStarFound == False:
		scoopableStarIndex = 'NONE'
		nextScoopableStar = 'NONE'
	return nextScoopableStar, scoopableStarIndex