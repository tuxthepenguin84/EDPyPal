# Calculates Fuel Levels & Capacity
def getFuel(edData):
	fuelLevel = round(edData.get('fuelLevel', 0))
	fuelCapacity = round(edData.get('fuelCapacity', 0))
	fuelPercent = round((fuelLevel/fuelCapacity)*100)
	fuelBar = '['
	for i in range(0, 250, 10):
		if i <= fuelPercent*2.5:
			fuelBar += '#'
		else:
			fuelBar += '-'
	fuelBar += ']'
	if fuelPercent >= 50:
		fuelBarColor = '1'
	elif fuelPercent < 50 and fuelPercent > 25:
		fuelBarColor = 'orange'
	elif fuelPercent <= 25:
		fuelBarColor = 'lightcoral'
	fuelPercent = str(fuelPercent)+'%'

	return fuelBar, fuelPercent, fuelBarColor, str(fuelLevel), str(fuelCapacity)