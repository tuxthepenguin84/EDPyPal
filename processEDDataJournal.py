def processEDDataJournal(newJournalData, argslocale, argsshutdown):
	# Modules
	import json
	import locale

	# Set Locale
	locale.setlocale(locale.LC_ALL, argslocale)

	# Initialize Variables
	edJournalData = {}
	currentMode = 'ModeDocked'
	minRequiredData = False
	edJournalData['fleetCarriers'] = []
	for journalLine in newJournalData:
		journalJson = json.loads(journalLine)
		if journalJson['event'] == 'Commander':
			edJournalData['cmdrName'] = journalJson['Name'].title()
		elif journalJson['event'] == 'Rank':
			Combat = ['Harmless', 'Mostly Harmless', 'Novice', 'Competent', 'Expert', 'Master', 'Dangerous', 'Deadly', 'Elite', 'Elite I', 'Elite II', 'Elite III', 'Elite IV', 'Elite V']
			Trader = ['Penniless', 'Mostly Penniless', 'Peddler', 'Dealer', 'Merchant', 'Broker', 'Entrepreneur', 'Tycoon', 'Elite', 'Elite I', 'Elite II', 'Elite III', 'Elite IV', 'Elite V']
			Explorer = ['Aimless', 'Mostly Aimless', 'Scout', 'Surveyor', 'Trailblazer', 'Pathfinder', 'Ranger', 'Pioneer', 'Elite', 'Elite I', 'Elite II', 'Elite III', 'Elite IV', 'Elite V']
			Soldier = ['Defenceless', 'Mostly Defenceless', 'Rookie', 'Soldier', 'Gunslinger', 'Warrior', 'Gladiator', 'Deadeye', 'Elite', 'Elite I', 'Elite II', 'Elite III', 'Elite IV', 'Elite V']
			Exobiologist = ['Directionless', 'Mostly Directionless', 'Compiler', 'Collector', 'Cataloguer', 'Taxonomist', 'Ecologist', 'Geneticist', 'Elite', 'Elite I', 'Elite II', 'Elite III', 'Elite IV', 'Elite V']
			Empire = ['None', 'Outsider', 'Serf', 'Master', 'Squire', 'Knight', 'Lord', 'Baron', 'Viscount', 'Count', 'Earl', 'Marquis', 'Duke', 'Prince', 'King']
			Federation = ['None', 'Recruit', 'Cadet', 'Midshipman', 'Petty Officer', 'Chief Petty Officer', 'Warrant Officer', 'Ensign', 'Lieutenant', 'Lieutenant Commander', 'Post Commander', 'Post Captain', 'Rear Admiral', 'Vice Admiral', 'Admiral']
			cqc = ['None', 'Outsider', 'Serf', 'Master', 'Squire', 'Knight', 'Lord', 'Baron', 'Viscount', 'Count', 'Earl', 'Marquis', 'Duke', 'Prince', 'King']
			edJournalData['rankCombat'] = Combat[journalJson['Combat']]
			edJournalData['rankTrade'] = Trader[journalJson['Trade']]
			edJournalData['rankExplore'] = Explorer[journalJson['Explore']]
			edJournalData['rankSoldier'] = Soldier[journalJson['Soldier']]
			edJournalData['rankExobiologist'] = Exobiologist[journalJson['Exobiologist']]
			edJournalData['rankEmpire'] = Empire[journalJson['Empire']]
			edJournalData['rankFederation'] = Federation[journalJson['Federation']]
			edJournalData['rankCQC'] = cqc[journalJson['CQC']]
		elif journalJson['event'] == 'LoadGame':
			edJournalData['cmdrName'] = journalJson['Commander'].title()
			edJournalData['ship'] = journalJson.get('Ship_Localised', journalJson['Ship'])
			edJournalData['shipName'] = journalJson['ShipName']
			edJournalData['fuelCapacity'] = round(journalJson['FuelCapacity'], 1)
			edJournalData['gameMode'] = journalJson['GameMode']
		elif journalJson['event'] == 'Location':
			if journalJson['Docked'] == True:
				currentMode = 'ModeDocked'
			elif journalJson['Docked'] == False:
				currentMode = 'ModeNavRoute'
			edJournalData['stationName'] = journalJson.get('StationName', '-')
			edJournalData['stationType'] = journalJson.get('StationType', '-')
			edJournalData['stationEconomy'] = journalJson.get('StationEconomy_Localised', '-')
			edJournalData['stationGovernment'] = journalJson.get('StationGovernment_Localised', '-')
			edJournalData['stationAllegiance'] = journalJson.get('StationAllegiance', '-')
			edJournalData['StationServices'] = journalJson.get('StationServices', '-')
			edJournalData['StationServices'] = journalJson.get('DistFromStarLS', '-')
			edJournalData['stationDistFromStarLS'] = locale.format_string('%d', round(journalJson.get('DistFromStarLS', 0), 1), grouping=True)
			edJournalData['starSystem'] = journalJson['StarSystem']
			edJournalData['systemAllegiance'] = journalJson['SystemAllegiance']
			edJournalData['systemEconomy'] = journalJson['SystemEconomy_Localised']
			edJournalData['systemSecondEconomy'] = journalJson['SystemSecondEconomy_Localised']
			edJournalData['systemGovernment'] = journalJson['SystemGovernment_Localised']
			edJournalData['systemSecurity'] = journalJson['SystemSecurity_Localised']
			edJournalData['systemPopulation'] = locale.format_string('%d', journalJson['Population'], grouping=True)
			edJournalData['systemGovernment'] = journalJson['SystemGovernment_Localised']
		elif journalJson['event'] == 'Loadout':
			edJournalData['shipName'] = journalJson['ShipName']
			edJournalData['shipIdent'] = journalJson['ShipIdent']
			edJournalData['shipValue'] = locale.format_string('%d', journalJson.get('HullValue', 0) + journalJson.get('ModulesValue', 0), grouping=True)
			edJournalData['shipUnladenMass'] = round(journalJson['UnladenMass'], 1)
			edJournalData['cargoCapacity'] = str(journalJson['CargoCapacity'])
			edJournalData['maxJumpRange'] = str(round(journalJson['MaxJumpRange'], 1))
			edJournalData['fuelCapacity'] = round(journalJson['FuelCapacity']['Main'], 1)
			edJournalData['rebuy'] = locale.format_string('%d', journalJson['Rebuy'], grouping=True)
			edJournalData['modules'] = journalJson['Modules']
			minRequiredData = True
		elif journalJson['event'] == 'ShipyardSwap':
			edJournalData['ship'] = journalJson.get('ShipType_Localised', None)
			if edJournalData['ship'] == None:
				edJournalData['ship'] = journalJson['ShipType']
			edJournalData['shipName'] = ''
			edJournalData['shipIdent'] = ''
		elif journalJson['event'] == 'FuelScoop':
			currentMode = 'ModeNavRoute'
		elif journalJson['event'] == 'Cargo':
			edJournalData['currentCargo'] = str(journalJson['Count'])
			edJournalData['currentInventory'] = json.dumps(journalJson.get('Inventory', ''))
		elif journalJson['event'] == 'Undocked':
			currentMode = 'ModeNavRoute'
		elif journalJson['event'] == 'Docked':
			currentMode = 'ModeDocked'
			edJournalData['stationName'] = journalJson['StationName']
			edJournalData['stationType'] = journalJson['StationType']
			edJournalData['starSystem'] = journalJson['StarSystem']
			#edJournalData['stationFaction'] = journalJson['StationFaction']['FactionState']
			edJournalData['stationEconomy'] = journalJson['StationEconomy_Localised']
			edJournalData['stationGovernment'] = journalJson['StationGovernment_Localised']
			edJournalData['stationAllegiance'] = journalJson.get('StationAllegiance', '-')
			edJournalData['stationServices'] = journalJson['StationServices']
			edJournalData['stationDistFromStarLS'] = locale.format_string('%d', round(journalJson['DistFromStarLS'], 1), grouping=True)
			edJournalData['stationLandingPads'] = []
			if journalJson['LandingPads']['Small'] > 0:
				edJournalData['stationLandingPadsS'] = 'S'
			elif journalJson['LandingPads']['Small'] == 0:
				edJournalData['stationLandingPadsS'] = '-'
			if journalJson['LandingPads']['Medium'] > 0:
				edJournalData['stationLandingPadsM'] = 'M'
			elif journalJson['LandingPads']['Medium'] == 0:
				edJournalData['stationLandingPadsM'] = '-'
			if journalJson['LandingPads']['Large'] > 0:
				edJournalData['stationLandingPadsL'] = 'L'
			elif journalJson['LandingPads']['Large'] == 0:
				edJournalData['stationLandingPadsL'] = '-'
		elif journalJson['event'] == 'FSDJump':
			currentMode = 'ModeNavRoute'
			edJournalData['fleetCarriers'] = []
			edJournalData['starSystem'] = journalJson['StarSystem']
			edJournalData['systemAllegiance'] = journalJson['SystemAllegiance']
			edJournalData['systemEconomy'] = journalJson['SystemEconomy_Localised']
			edJournalData['systemSecondEconomy'] = journalJson['SystemSecondEconomy_Localised']
			edJournalData['systemGovernment'] = journalJson['SystemGovernment_Localised']
			edJournalData['systemSecurity'] = journalJson['SystemSecurity_Localised']
			edJournalData['systemPopulation'] = locale.format_string('%d', journalJson['Population'], grouping=True)
			edJournalData['systemGovernment'] = journalJson['SystemGovernment_Localised']
		elif journalJson['event'] == 'FSSDiscoveryScan':
			currentMode = 'ModeNavRoute'
			edJournalData['fssdsProgress'] = journalJson['Progress']
			edJournalData['fssdsBodyCount'] = journalJson['BodyCount']
			edJournalData['fssdsNonBodyCount'] = journalJson['NonBodyCount']
			edJournalData['fssdsSystemName'] = journalJson.get('SystemName', None)
		elif journalJson['event'] == 'FSSAllBodiesFound':
			currentMode = 'ModeNavRoute'
			edJournalData['fssdsSystemName'] = journalJson.get('SystemName', None)
			edJournalData['fssdsProgress'] = 1.000000
			edJournalData['fssdsBodyCount'] = journalJson['Count']
		elif journalJson['event'] == 'FSSSignalDiscovered':
			if journalJson.get('IsStation', False) == True:
				edJournalData['fleetCarriers'].append(journalJson['SignalName'])
		elif journalJson['event'] == 'StartJump':
			currentMode = 'ModeNavRoute'
		elif journalJson['event'] == 'SupercruiseEntry':
			currentMode = 'ModeNavRoute'
		elif journalJson['event'] == 'Shutdown':
			print('SHUTDOWN: Game reached shutdown, shutting down EDPyPal now...')
			if argsshutdown == True:
				quit()

	return edJournalData, currentMode, minRequiredData