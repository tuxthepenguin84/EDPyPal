# Modules
import os
import json

# Initialize Variables
debugImportEDDBIO = 'IMPORT-EDDBIO:'

def importEDDBIOData():
    try:
        # Import Systems Data
        systemsPopPath = os.environ['USERPROFILE'] + '/Saved Games/Frontier Developments/Elite Dangerous/systems_populated.json'
        with open(systemsPopPath, 'r') as systemsPopPathFile:
            print(debugImportEDDBIO, 'Loading ', systemsPopPath)
            systemsPopData = json.load(systemsPopPathFile)
        systemsPopPathFile.close()
        print(debugImportEDDBIO, 'Finished Reading', systemsPopPath)
    except FileNotFoundError:
        systemsPopData = None
    
    try:
        # Import Stations Data
        stationsPath = os.environ['USERPROFILE'] + '/Saved Games/Frontier Developments/Elite Dangerous/stations.json'
        with open(stationsPath, 'r') as stationsPathFile:
            print(debugImportEDDBIO, 'Loading ', stationsPath)
            stationsData = json.load(stationsPathFile)
        stationsPathFile.close()
        print(debugImportEDDBIO, 'Finished Reading', stationsPath)
    except FileNotFoundError:
        stationsData = None

    try:
        # Import Modules Data
        modulesPath = os.environ['USERPROFILE'] + '/Saved Games/Frontier Developments/Elite Dangerous/modules.json'
        with open(modulesPath, 'r') as modulesPathFile:
            print(debugImportEDDBIO, 'Loading ', modulesPath)
            modulesData = json.load(modulesPathFile)
        modulesPathFile.close()
        print(debugImportEDDBIO, 'Finished Reading', modulesPath)
    except FileNotFoundError:
        modulesData = None
    
    # Return Imported Data
    return systemsPopData, stationsData, modulesData