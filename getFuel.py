# Calculates Fuel Levels & Capacity
def getFuel(processedJournalData, processedStatusData):
	fuelLevel = round(processedStatusData.get('fuelLevel', 0))
	fuelCapacity = round(processedJournalData.get('fuelCapacity', 0))
	fuelPercent = round((fuelLevel/fuelCapacity)*100)
	fuelBar = '['
	for i in range(0, 250, 10):
		if i <= fuelPercent*2.5:
			fuelBar += '#'
		else:
			fuelBar += '-'
	fuelBar += ']'
	if fuelPercent > 50:
		fuelBarColor = '1' # White
	elif fuelPercent <= 50 and fuelPercent >= 25:
		fuelBarColor = 'orange'
	elif fuelPercent < 25 and fuelPercent >= 10:
		fuelBarColor = 'lightcoral'
	elif fuelPercent < 10:
		fuelBarColor = 'lightcoral'
		fuelBar = 'fuelrats.com'
	fuelPercent = str(fuelPercent)+'%'

	return fuelBar, fuelPercent, fuelBarColor, str(fuelLevel), str(fuelCapacity)