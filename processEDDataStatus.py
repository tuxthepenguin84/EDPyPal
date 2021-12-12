def processEDDataStatus(importedStatusData):
	# Initialize Variables
	processedStatusData = {}
	
	# Status.json
	processedStatusData['credits'] = importedStatusData.get('Balance', 0)
	try:
		processedStatusData['fuelLevel'] = round(importedStatusData['Fuel']['FuelMain'], 1)
	except KeyError:
		processedStatusData['fuelLevel'] = 0

	return processedStatusData