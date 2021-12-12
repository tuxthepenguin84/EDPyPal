# Modules
import os

def importEDDataJournal(edRootPath):
	debugImportEDData = 'IMPORT-EDDATA-Journal:'
	journalPath = list(edRootPath.glob('Journal*.log'))[-1]
	with open(journalPath, 'r') as journalPathFile:
		print(debugImportEDData, 'Loading', journalPath)
		importedJournalData = journalPathFile.readlines()
	journalPathFile.close()
	print(debugImportEDData, 'Finished Reading', journalPath)
	journalPathModTime = os.stat(journalPath).st_mtime

	return importedJournalData, journalPathModTime, journalPath