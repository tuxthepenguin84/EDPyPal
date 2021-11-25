# Modules
import os
import json
import time
from pathlib import Path

# Initialize Variables
debugImportEDData = 'IMPORT-EDDATA:'

def importEDData():
	navRoutePath = os.environ['USERPROFILE'] + '/Saved Games/Frontier Developments/Elite Dangerous/NavRoute.json'
	with open(navRoutePath, 'r') as navRoutePathFile:
		print(debugImportEDData, 'Loading', navRoutePath)
		try:
			navRouteData = json.load(navRoutePathFile)
		except json.decoder.JSONDecodeError:
			print('ERROR: Retrying JSON File')
			time.sleep(1)
			navRouteData = json.load(navRoutePathFile)
	navRoutePathFile.close()
	print(debugImportEDData, 'Finished Reading', navRoutePath)
	navRoutePathModTime = os.stat(navRoutePath).st_mtime

	edRootPath = Path(os.environ['USERPROFILE'] + '/Saved Games/Frontier Developments/Elite Dangerous/')
	newJournalPath = list(edRootPath.glob('Journal*.log'))[-1]
	with open(newJournalPath, 'r') as newJournalPathFile:
		print(debugImportEDData, 'Loading', newJournalPath)
		newJournalData = newJournalPathFile.readlines()
	newJournalPathFile.close()
	print(debugImportEDData, 'Finished Reading', newJournalPath)
	newJournalPathModTime = os.stat(newJournalPath).st_mtime

	return navRouteData, navRoutePathModTime, navRoutePath, newJournalData, newJournalPathModTime, newJournalPath