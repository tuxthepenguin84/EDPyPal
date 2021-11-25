def processEDData(newJournalData, userLocale):
	# Modules
	import json
	import locale

	# Set Locale
	locale.setlocale(locale.LC_ALL, userLocale)

	# Initialize Variables
	edData = {}
	currentMode = 'ModeDocked'
	minRequiredData = False
	for journalLine in newJournalData:
		journalJson = json.loads(journalLine)
		if journalJson['event'] == 'Commander':
			edData['cmdrName'] = journalJson['Name'].title()
		elif journalJson['event'] == 'Rank':
			Combat = ['Harmless', 'Mostly Harmless', 'Novice', 'Competent', 'Expert', 'Master', 'Dangerous', 'Deadly', 'Elite', 'Elite I', 'Elite II', 'Elite III', 'Elite IV', 'Elite V']
			Trader = ['Penniless', 'Mostly Penniless', 'Peddler', 'Dealer', 'Merchant', 'Broker', 'Entrepreneur', 'Tycoon', 'Elite', 'Elite I', 'Elite II', 'Elite III', 'Elite IV', 'Elite V']
			Explorer = ['Aimless', 'Mostly Aimless', 'Scout', 'Surveyor', 'Trailblazer', 'Pathfinder', 'Ranger', 'Pioneer', 'Elite', 'Elite I', 'Elite II', 'Elite III', 'Elite IV', 'Elite V']
			edData['rankCombat'] = Combat[journalJson['Combat']]
			edData['rankTrade'] = Trader[journalJson['Trade']]
			edData['rankExplore'] = Explorer[journalJson['Explore']]
		elif journalJson['event'] == 'LoadGame':
			edData['cmdrName'] = journalJson['Commander'].title()
			edData['ship'] = journalJson.get('Ship_Localised', journalJson['Ship'])
			edData['shipName'] = journalJson['ShipName']
			edData['fuelLevel'] = round(journalJson['FuelLevel'], 1)
			edData['fuelCapacity'] = round(journalJson['FuelCapacity'], 1)
			edData['gameMode'] = journalJson['GameMode']
			edData['credits'] = journalJson['Credits']
			edData['cmdrName'] = journalJson['Commander']
			edData['cmdrName'] = journalJson['Commander']
		elif journalJson['event'] == 'Location':
			if journalJson['Docked'] == True:
				currentMode = 'ModeDocked'
			elif journalJson['Docked'] == False:
				currentMode = 'ModeNavRoute'
			edData['stationName'] = journalJson.get('StationName', '-')
			edData['stationType'] = journalJson.get('StationType', '-')
			edData['stationEconomy'] = journalJson.get('StationEconomy_Localised', '-')
			edData['stationGovernment'] = journalJson.get('StationGovernment_Localised', '-')
			edData['stationAllegiance'] = journalJson.get('StationAllegiance', '-')
			edData['StationServices'] = journalJson.get('StationServices', '-')
			edData['StationServices'] = journalJson.get('DistFromStarLS', '-')
			edData['stationDistFromStarLS'] = locale.format_string('%d', round(journalJson.get('DistFromStarLS', 0), 1), grouping=True)
			edData['starSystem'] = journalJson['StarSystem']
			edData['systemAllegiance'] = journalJson['SystemAllegiance']
			edData['systemEconomy'] = journalJson['SystemEconomy_Localised']
			edData['systemSecondEconomy'] = journalJson['SystemSecondEconomy_Localised']
			edData['systemGovernment'] = journalJson['SystemGovernment_Localised']
			edData['systemSecurity'] = journalJson['SystemSecurity_Localised']
			edData['systemPopulation'] = locale.format_string('%d', journalJson['Population'], grouping=True)
			edData['systemGovernment'] = journalJson['SystemGovernment_Localised']
		elif journalJson['event'] == 'Loadout':
			#edData['ship'] = journalJson['Ship']
			edData['shipName'] = journalJson['ShipName']
			edData['shipIdent'] = journalJson['ShipIdent']
			edData['shipValue'] = locale.format_string('%d', journalJson.get('HullValue', 0) + journalJson.get('ModulesValue', 0), grouping=True)
			edData['shipUnladenMass'] = round(journalJson['UnladenMass'], 1)
			edData['cargoCapacity'] = str(journalJson['CargoCapacity'])
			edData['maxJumpRange'] = str(round(journalJson['MaxJumpRange'], 1))
			edData['fuelCapacity'] = round(journalJson['FuelCapacity']['Main'], 1)
			edData['fuelLevel'] = edData['fuelCapacity']
			edData['rebuy'] = locale.format_string('%d', journalJson['Rebuy'], grouping=True)
			edData['modules'] = journalJson['Modules']
			minRequiredData = True
		elif journalJson['event'] == 'ShipyardSwap':
			edData['ship'] = journalJson.get('ShipType_Localised', None)
			if edData['ship'] == None:
				edData['ship'] = journalJson['ShipType']
			edData['shipName'] = ''
			edData['shipIdent'] = ''
		elif journalJson['event'] == 'RefuelAll':
			edData['credits'] = edData['credits'] - journalJson['Cost']
			edData['fuelLevel'] = edData['fuelCapacity']
		elif journalJson['event'] == 'FuelScoop':
			currentMode = 'ModeNavRoute'
			edData['fuelLevel'] = journalJson['Total']
		elif journalJson['event'] == 'RepairAll':
			edData['credits'] = edData['credits'] - journalJson['Cost']
		elif journalJson['event'] == 'Repair':
			edData['credits'] = edData['credits'] - journalJson['Cost']
		elif journalJson['event'] == 'MissionCompleted':
			edData['credits'] = edData['credits'] + journalJson.get('Reward', 0)
			edData['credits'] = edData['credits'] - journalJson.get('Donated', 0)
		elif journalJson['event'] == 'ModuleBuy':
			edData['credits'] = edData['credits'] + journalJson.get('SellPrice', 0)
			edData['credits'] = edData['credits'] - journalJson.get('BuyPrice', 0)
		elif journalJson['event'] == 'MarketBuy':
			edData['credits'] = edData['credits'] - journalJson['TotalCost']
		elif journalJson['event'] == 'MarketSell':
			edData['credits'] = edData['credits'] + journalJson['TotalSale']
		elif journalJson['event'] == 'MultiSellExplorationData':
			edData['credits'] = edData['credits'] + journalJson['TotalEarnings']
		elif journalJson['event'] == 'Cargo':
			edData['currentCargo'] = str(journalJson['Count'])
			edData['currentInventory'] = json.dumps(journalJson.get('Inventory', ''))
		elif journalJson['event'] == 'Undocked':
			currentMode = 'ModeNavRoute'
		elif journalJson['event'] == 'Docked':
			currentMode = 'ModeDocked'
			edData['stationName'] = journalJson['StationName']
			edData['stationType'] = journalJson['StationType']
			edData['starSystem'] = journalJson['StarSystem']
			#edData['stationFaction'] = journalJson['StationFaction']['FactionState']
			edData['stationEconomy'] = journalJson['StationEconomy_Localised']
			edData['stationGovernment'] = journalJson['StationGovernment_Localised']
			edData['stationAllegiance'] = journalJson.get('StationAllegiance', '-')
			edData['stationServices'] = journalJson['StationServices']
			edData['stationDistFromStarLS'] = locale.format_string('%d', round(journalJson['DistFromStarLS'], 1), grouping=True)
			edData['stationLandingPads'] = []
			if journalJson['LandingPads']['Small'] > 0:
				edData['stationLandingPadsS'] = 'S'
			elif journalJson['LandingPads']['Small'] == 0:
				edData['stationLandingPadsS'] = '-'
			if journalJson['LandingPads']['Medium'] > 0:
				edData['stationLandingPadsM'] = 'M'
			elif journalJson['LandingPads']['Medium'] == 0:
				edData['stationLandingPadsM'] = '-'
			if journalJson['LandingPads']['Large'] > 0:
				edData['stationLandingPadsL'] = 'L'
			elif journalJson['LandingPads']['Large'] == 0:
				edData['stationLandingPadsL'] = '-'
		elif journalJson['event'] == 'FSDJump':
			currentMode = 'ModeNavRoute'
			edData['starSystem'] = journalJson['StarSystem']
			edData['systemAllegiance'] = journalJson['SystemAllegiance']
			edData['systemEconomy'] = journalJson['SystemEconomy_Localised']
			edData['systemSecondEconomy'] = journalJson['SystemSecondEconomy_Localised']
			edData['systemGovernment'] = journalJson['SystemGovernment_Localised']
			edData['systemSecurity'] = journalJson['SystemSecurity_Localised']
			edData['systemPopulation'] = locale.format_string('%d', journalJson['Population'], grouping=True)
			edData['systemGovernment'] = journalJson['SystemGovernment_Localised']
			edData['fuelLevel'] = journalJson['FuelLevel']
		elif journalJson['event'] == 'ReservoirReplenished':
			edData['fuelLevel'] = journalJson['FuelMain']
		elif journalJson['event'] == 'FSSDiscoveryScan':
			currentMode = 'ModeNavRoute'
			edData['fssdsProgress'] = journalJson['Progress']
			edData['fssdsBodyCount'] = journalJson['BodyCount']
			edData['fssdsNonBodyCount'] = journalJson['NonBodyCount']
		elif journalJson['event'] == 'FSSAllBodiesFound':
			currentMode = 'ModeNavRoute'
			edData['fssdsProgress'] = 1.000000
			edData['fssdsBodyCount'] = journalJson['Count']
		elif journalJson['event'] == 'StartJump':
			currentMode = 'ModeNavRoute'
		elif journalJson['event'] == 'SupercruiseEntry':
			currentMode = 'ModeNavRoute'
	return edData, currentMode, minRequiredData