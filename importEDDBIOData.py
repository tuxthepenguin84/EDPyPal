# Modules
import json

# Initialize Variables
debugImportEDDBIO = 'IMPORT-EDDBIO:'

def importEDDBIOData(eddbJSONFile, edRootPath):
    try:
        eddbJSONFilePath = str(edRootPath) + '/' + eddbJSONFile
        with open(eddbJSONFilePath, 'r') as eddbJSONFilePathFile:
            print(debugImportEDDBIO, 'Loading ', eddbJSONFilePath)
            eddbJSONFileData = json.load(eddbJSONFilePathFile)
        eddbJSONFilePathFile.close()
        print(debugImportEDDBIO, 'Finished Reading', eddbJSONFilePath)
    except FileNotFoundError:
        eddbJSONFileData = None
    
    # Return Imported Data
    return eddbJSONFileData