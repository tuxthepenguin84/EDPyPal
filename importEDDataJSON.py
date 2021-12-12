# Modules
import os
import json
import time

# Example jsonFile passed through: Status, Market, ModulesInfo
def importEDDataJSON(jsonFile, edRootPath):
	debugImportEDData = 'IMPORT-EDDATA-' + jsonFile + ':'
	jsonFileData = None
	jsonFilePath = str(edRootPath) + '/' + jsonFile + '.json'
	with open(jsonFilePath, 'r') as jsonFilePathFile:
		print(debugImportEDData, 'Loading', jsonFilePath)
		while jsonFileData == None:
			try:
				jsonFileData = json.load(jsonFilePathFile)
			except json.decoder.JSONDecodeError:
				print('ERROR: JSONDecodeError - Retrying ' + jsonFile + '.json File')
				time.sleep(1)
	jsonFilePathFile.close()
	print(debugImportEDData, 'Finished Reading', jsonFilePath)
	jsonFilePathModTime = os.stat(jsonFilePath).st_mtime

	return jsonFileData, jsonFilePathModTime, jsonFilePath