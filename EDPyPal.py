# Modules
import argparse
import locale
import math
import matplotlib.pyplot as plt
import os
from pathlib import Path
import sys
import time

# Custom Modules
from importEDDataJSON import * # Loads & Imports JSON function
from importEDDataJournal import * # Loads & Imports Journal function
from processEDDataJournal import * # Processes data from Journal*.log
from processEDDataStatus import * # Processes data from Status JSON
from importEDDBIOData import * # Imports station & system data from EDDB.io, place files (systems_populated.json & stations.json) in ED folder
from findSystemInRoute import * # Find Current System In Route
from closestSystemServices import * # Find Closest System Services
from getNextScoopableStar import * # Find Next Scoopable Star
from getFuel import * # Calculates Fuel Levels & Capacity
from getShipModules import * # Find All Ship Modules

# Remove matplotlib toolbar
plt.rcParams['toolbar'] = 'None'

# CLI Arguments
parser = argparse.ArgumentParser(description='EDPyPal')
parser.add_argument("-m", "--mode", help="Manual mode override. | Example: ModeNaveRoute or ModeDocked ", nargs=1, default=None)
parser.add_argument("-w", "--window", help="Window geometry location. | Example: +2552+0", nargs=1, default='+0+0')
parser.add_argument("-l", "--locale", help="Set locale. | Example : en_US", nargs=1, default='en_US')
parser.add_argument("-s", "--shutdown", help="Stop EDPyPal after ED shutdown.", default=False, action='store_true')
parser.add_argument("-v", "--version", help="Show version info and quit.", default=False, action='store_true')
args = parser.parse_args()
print(args)

# Version
print('EDPyPal 0.1.2')
if args.version == True:
	quit()

# Set Locale
locale.setlocale(locale.LC_ALL, args.locale)

# Watch for keypress events
def on_press(event):
	# Force Flush Buffer in Python
	sys.stdout.flush()

	# Global Variables
	global manualModeRequest
	global navRoutePathModTime
	global journalPathModTime

	# Initialize Variables
	debugOnPress = 'KEY PRESS:'

	# Quit application
	if event.key == 'escape' or event.key == 'q':
		print(debugOnPress, 'Quitting...', event.key)
		plt.close('all')
		quit()
	# Refresh screen while in NavRoute mode
	elif event.key == 'r':
		print(debugOnPress, 'Refreshing...', event.key)
		global refreshRequested
		refreshRequested = True
	# Pause rotating route plot while in NavRoute mode
	elif event.key == 'p':
		print(debugOnPress, 'Pausing...', event.key)
		global pauseRequested
		if pauseRequested == False:
			pauseRequested = True
		elif pauseRequested == True:
			pauseRequested = False
		print(pauseRequested)
	# Auto Mode (default) switches views based on events in game (docking, undocking, FSD jump, etc.)
	elif event.key == '0':
		manualModeRequest = None
		Path(journalPath).touch() # Quickly trigger Journal File Change
		print(debugOnPress, 'Auto Mode Requested...')
	# Manually switch to Docked Mode, view will not change unless switched back to Auto Mode or another manual mode
	elif event.key == '1':
		manualModeRequest = 'ModeDocked'
		print (debugOnPress, 'Manual Mode Requested:', manualModeRequest)
	# Manually switch to NavRoute Mode, view will not change unless switched back to Auto Mode or another manual mode
	elif event.key == '2':
		manualModeRequest = 'ModeNavRoute'
		print (debugOnPress, 'Manual Mode Requested:', manualModeRequest)

def pltFigure():
	fig = plt.figure(num='EDPyPal') # Window Title
	fig.patch.set_facecolor('black') # Background Color
	fig.set_figwidth(984/96) # Pixels / DPI = Inches
	fig.set_figheight(1280/96) # https://www.infobyip.com/detectmonitordpi.php
	fig.canvas.mpl_connect('key_press_event', on_press) # Configure to watch for key presses
	return fig

def pltAxes():
	plt.clf() # Clear figure
	ax = fig.add_subplot(projection='3d')
	ax.patch.set_alpha(0) # Set Alpha
	ax.axes.get_xaxis().set_ticks([])
	ax.axes.get_yaxis().set_ticks([])
	ax.axes.get_zaxis().set_ticks([])
	fig.tight_layout() # Tighten Layout
	plt.axis('off') # Hide Axis
	plt.get_current_fig_manager().window.wm_geometry(args.window) # Set Window Geometry
	#plt.get_current_fig_manager().window.state('zoomed') # Optionally open fullscreen on primary monitor
	return ax

def modeNavRoute(processedJournalData, journalPathModTime, journalPath, processedStatusData, statusPathModTime, statusPath):
	# Global Variables
	global currentMode
	global refreshRequested
	global pauseRequested
	global manualModeRequest

	# Initialize Variables
	debugmodeNavRoute = 'NAVROUTE:'
	currentMode = 'ModeNavRoute'
	restartModeNavRoute = False
	exitModeNavRoute = False
	refreshRequested = False
	pauseRequested = False

	###########################
	## Gather Nav Route Data ##
	###########################

	# Find Current System
	print(debugmodeNavRoute, 'Current Route:', importedNavRouteData['Route'])
	currentSystem = processedJournalData['starSystem']
	print(debugmodeNavRoute, 'Current System:', currentSystem)

	# Find Current System In Route
	scoop = 'orange' # Color of Star Text that is Scoopable
	nonScoop = 'red' # Color of Star Text that is nonScoopable
	scoopMapping = {'O' : scoop, 'B' : scoop, 'A' : scoop, 'F' : scoop, 'G': scoop, 'K': scoop, 'M': scoop, 'S': nonScoop, 'TTS': nonScoop, 'Y': nonScoop, 'L': nonScoop, 'T': nonScoop, 'DA': nonScoop}
	xStarPos, yStarPos, zStarPos, starClass, starSystem, routeLength, visibleRouteLength = findSystemInRoute(importedNavRouteData, ax, currentSystem, scoop, nonScoop, scoopMapping)
	print(debugmodeNavRoute, xStarPos, yStarPos, zStarPos, starClass, starSystem)
	print(debugmodeNavRoute, 'Route Length - ', routeLength)
	print(debugmodeNavRoute, 'Visible Route Length - ', visibleRouteLength)

	# Find Closest System Services
	stationServices, allStations = closestSystemServices(processedJournalData['starSystem'], systemsPopData, stationsData)
	print(debugmodeNavRoute, 'Station Services:', stationServices)
	print(debugmodeNavRoute, 'All Stations:', allStations, len(allStations))

	# Find Next Scoopable Star
	if starSystem != []:
		nextScoopableStar, scoopableStarIndex = getNextScoopableStar(starClass, scoopMapping, scoop, starSystem)
		print(debugmodeNavRoute, nextScoopableStar, scoopableStarIndex)
	else:
		nextScoopableStar = ''

	# Calculates Fuel Levels & Capacity
	fuelBar, fuelPercent, fuelBarColor, fuelLevel, fuelCapacity = getFuel(processedJournalData, processedStatusData)
	print(debugmodeNavRoute, fuelBar, fuelPercent, '%')

	#############
	## 2D Text ##
	#############

	# Text Sizes
	ModeNavRouteTitleTextSize = 'large'
	ModeNavRouteNavTextSize = 'small'
	ModeNavRouteBottomMainTextSize = 'medium'
	ModeNavRouteBottomMinorTextSize = 'small'
	ModeNavRouteStationServicesTextSize = 'medium'

	# Mode
	ax.text2D(0.99, 0.99, ('Nav Mode') , color='1', fontsize=ModeNavRouteTitleTextSize, horizontalalignment='right', fontweight='bold', transform=ax.transAxes)

	# Help
	#ax.text2D(0.99, 0.99, ('(f) Fullscreen'), color='1', fontsize='x-small', horizontalalignment='left', transform=ax.transAxes)
	#ax.text2D(0.99, 0.97, ('(p) Pause'), color='1', fontsize='x-small', horizontalalignment='left', transform=ax.transAxes)
	#ax.text2D(0.99, 0.95, ('(r) Refresh'), color='1', fontsize='x-small', horizontalalignment='left', transform=ax.transAxes)
	#ax.text2D(0.99, 0.93, ('(Escape) Quit'), color='1', fontsize='x-small', horizontalalignment='left', transform=ax.transAxes)

	# Fuel
	fuel = ax.text2D(0.50, 0.99, 'Fuel ' + fuelLevel + '/' + fuelCapacity + ' T', color='1', fontsize='medium', horizontalalignment='center', transform=ax.transAxes)
	fuel2dBar = ax.text2D(0.50, 0.97, fuelBar + ' ' + fuelPercent, color=fuelBarColor, fontsize='medium', fontfamily='monospace', fontweight='bold', horizontalalignment='center', transform=ax.transAxes)
	ax.text2D(0.50, 0.95, 'Next Fuel Star - ' + nextScoopableStar, color='1', fontsize='medium', horizontalalignment='center', transform=ax.transAxes)

	# Services
	if stationServices != None:
		stationServiceStartingX = 0.01
		stationServiceStartingY = 0.99
		stationServiceInc = 0.02
		if stationServices['has_refuel'] != None:
			ax.text2D(stationServiceStartingX, stationServiceStartingY, 'Refuel - ' + stationServices['has_refuel']['Name'] + ' ' + str(stationServices['has_refuel']['Distance (LS)']) + ' LS' + ' (' + stationServices['has_refuel']['Landing Pad'] + ')', color='1', fontsize=ModeNavRouteStationServicesTextSize, horizontalalignment='left', transform=ax.transAxes); stationServiceStartingY -= stationServiceInc
		if stationServices['has_repair'] != None:
			ax.text2D(stationServiceStartingX, stationServiceStartingY, 'Repair - ' + stationServices['has_repair']['Name'] + ' ' + str(stationServices['has_repair']['Distance (LS)']) + ' LS' + ' (' + stationServices['has_repair']['Landing Pad'] + ')', color='1', fontsize=ModeNavRouteStationServicesTextSize, horizontalalignment='left', transform=ax.transAxes); stationServiceStartingY -= stationServiceInc
		if stationServices['has_rearm'] != None:
			ax.text2D(stationServiceStartingX, stationServiceStartingY, 'Rearm - ' + stationServices['has_rearm']['Name'] + ' ' + str(stationServices['has_rearm']['Distance (LS)']) + ' LS' + ' (' + stationServices['has_rearm']['Landing Pad'] + ')', color='1', fontsize=ModeNavRouteStationServicesTextSize, horizontalalignment='left', transform=ax.transAxes); stationServiceStartingY -= stationServiceInc
		if stationServices['has_outfitting'] != None:
			ax.text2D(stationServiceStartingX, stationServiceStartingY, 'Outfitting - ' + stationServices['has_outfitting']['Name'] + ' ' + str(stationServices['has_outfitting']['Distance (LS)']) + ' LS' + ' (' + stationServices['has_outfitting']['Landing Pad'] + ')', color='1', fontsize=ModeNavRouteStationServicesTextSize, horizontalalignment='left', transform=ax.transAxes); stationServiceStartingY -= stationServiceInc
		if stationServices['has_shipyard'] != None:
			ax.text2D(stationServiceStartingX, stationServiceStartingY, 'Shipyard - ' + stationServices['has_shipyard']['Name'] + ' ' + str(stationServices['has_shipyard']['Distance (LS)']) + ' LS' + ' (' + stationServices['has_shipyard']['Landing Pad'] + ')', color='1', fontsize=ModeNavRouteStationServicesTextSize, horizontalalignment='left', transform=ax.transAxes); stationServiceStartingY -= stationServiceInc
		if stationServices['has_material_trader'] != None:
			ax.text2D(stationServiceStartingX, stationServiceStartingY, 'Material Trader - ' + stationServices['has_material_trader']['Name'] + ' ' + str(stationServices['has_material_trader']['Distance (LS)']) + ' LS' + ' (' + stationServices['has_material_trader']['Landing Pad'] + ')', color='1', fontsize=ModeNavRouteStationServicesTextSize, horizontalalignment='left', transform=ax.transAxes); stationServiceStartingY -= stationServiceInc
		if stationServices['has_technology_broker'] != None:
			ax.text2D(stationServiceStartingX, stationServiceStartingY, 'Tech Broker - ' + stationServices['has_technology_broker']['Name'] + ' ' + str(stationServices['has_technology_broker']['Distance (LS)']) + ' LS' + ' (' + stationServices['has_technology_broker']['Landing Pad'] + ')', color='1', fontsize=ModeNavRouteStationServicesTextSize, horizontalalignment='left', transform=ax.transAxes); stationServiceStartingY -= stationServiceInc

	# Current System
	ax.text2D(0.01, 0.07, 'Current System', color='1', fontsize='small', horizontalalignment='left', transform=ax.transAxes)
	ax.text2D(0.01, 0.05, processedJournalData['starSystem'], color='1', fontsize='large', fontweight='bold', horizontalalignment='left', transform=ax.transAxes)

	# Discovery Progress
	discovery = ax.text2D(0.01, 0.03, 'Discovery -% | Bodies - | NonBodies -', color='1', fontsize='medium', horizontalalignment='left', transform=ax.transAxes)
	fleetcarriers = ax.text2D(0.01, 0.01, 'Fleet Carriers ' + str(len(list(dict.fromkeys(processedJournalData['fleetCarriers'])))), color='1', fontsize='medium', horizontalalignment='left', transform=ax.transAxes)

	# Next System
	if routeLength > 1:
		ax.text2D(0.50, 0.07, 'Next System', color='1', fontsize='small', horizontalalignment='center', transform=ax.transAxes)
		ax.text2D(0.50, 0.05, starSystem[1], color='1', fontsize='large', fontweight='bold', horizontalalignment='center', transform=ax.transAxes)
	
	# Jumps to Destination
	if routeLength == 2:
		ax.text2D(0.50, 0.03, str(routeLength-1) + (' Jump to Destination'), color='1', fontsize='medium', horizontalalignment='center', transform=ax.transAxes)
	elif routeLength > 2:
		ax.text2D(0.50, 0.03, str(routeLength-1) + (' Jumps to Destination'), color='1', fontsize='medium', horizontalalignment='center', transform=ax.transAxes)
	
	# Destination System
	if routeLength > 1:
		ax.text2D(0.99, 0.07, 'Destination System', color='1', fontsize='small', horizontalalignment='right', transform=ax.transAxes)
		ax.text2D(0.99, 0.05, starSystem[-1], color='1', fontsize='large', fontweight='bold', horizontalalignment='right', transform=ax.transAxes)
	
	# 3D Plot/Route
	# Current/Next/Destination
	if routeLength > 11:
		ax.text(xStarPos[0]+3, yStarPos[0]+3, zStarPos[0]+3, starSystem[0], color='1', zorder=10, fontsize='medium', horizontalalignment='center', verticalalignment='bottom')
		ax.text(xStarPos[0]+3, yStarPos[0]+3, zStarPos[0]+3, '(Current)', color='1', zorder=10, fontsize='small', horizontalalignment='center', verticalalignment='top')
		ax.text(xStarPos[1]+3, yStarPos[1]+3, zStarPos[1]+3, starSystem[1], color='1', zorder=10, fontsize='medium', horizontalalignment='center', verticalalignment='bottom')
		ax.text(xStarPos[1]+3, yStarPos[1]+3, zStarPos[1]+3, '(Next)', color='1', zorder=10, fontsize='small', horizontalalignment='center', verticalalignment='top')
		ax.text(xStarPos[-2]+3, yStarPos[-2]+3, zStarPos[-2]+3, str(routeLength-11) + ' + ' + starSystem[-1], color='1', zorder=10, fontsize='medium', horizontalalignment='center', verticalalignment='bottom')
		ax.text(xStarPos[-2]+3, yStarPos[-2]+3, zStarPos[-2]+3, '(Destination)', color='1', zorder=10, fontsize='small', horizontalalignment='center', verticalalignment='top')
	elif routeLength > 2 and routeLength <= 11:
		ax.text(xStarPos[0] + visibleRouteLength*0.25, yStarPos[0] + visibleRouteLength*0.25, zStarPos[0] + visibleRouteLength*0.25, starSystem[0], color='1', zorder=10, fontsize='medium', horizontalalignment='center', verticalalignment='bottom')
		ax.text(xStarPos[0] + visibleRouteLength*0.25, yStarPos[0] + visibleRouteLength*0.25, zStarPos[0] + visibleRouteLength*0.25,'(Current)', color='1', zorder=10, fontsize='small', horizontalalignment='center', verticalalignment='top')
		ax.text(xStarPos[1] + visibleRouteLength*0.25, yStarPos[1] + visibleRouteLength*0.25, zStarPos[1] + visibleRouteLength*0.25, starSystem[1], color='1', zorder=10, fontsize='medium', horizontalalignment='center', verticalalignment='bottom')
		ax.text(xStarPos[1] + visibleRouteLength*0.25, yStarPos[1] + visibleRouteLength*0.25, zStarPos[1] + visibleRouteLength*0.25, '(Next)', color='1', zorder=10, fontsize='small', horizontalalignment='center', verticalalignment='top')
		ax.text(xStarPos[-1] + visibleRouteLength*0.25, yStarPos[-1] + visibleRouteLength*0.25, zStarPos[-1] + visibleRouteLength*0.25, starSystem[-1], color='1', fontsize='medium', zorder=10, horizontalalignment='center', verticalalignment='bottom')
		ax.text(xStarPos[-1] + visibleRouteLength*0.25, yStarPos[-1] + visibleRouteLength*0.25, zStarPos[-1] + visibleRouteLength*0.25, '(Destination)', color='1', fontsize='small', zorder=10, horizontalalignment='center', verticalalignment='top')
	elif routeLength == 2:
		ax.text(xStarPos[0] + visibleRouteLength*0.25, yStarPos[0] + visibleRouteLength*0.25, zStarPos[0] + visibleRouteLength*0.25, starSystem[0], color='1', zorder=10, fontsize='medium', horizontalalignment='center', verticalalignment='bottom')
		ax.text(xStarPos[0] + visibleRouteLength*0.25, yStarPos[0] + visibleRouteLength*0.25, zStarPos[0] + visibleRouteLength*0.25, '(Current)', color='1', zorder=10, fontsize='small', horizontalalignment='center', verticalalignment='top')
		ax.text(xStarPos[-1] + visibleRouteLength*0.25, yStarPos[-1] + visibleRouteLength*0.25, zStarPos[-1] + visibleRouteLength*0.25, starSystem[-1], color='1', zorder=10, fontsize='medium', horizontalalignment='center', verticalalignment='bottom')
		ax.text(xStarPos[-1] + visibleRouteLength*0.25, yStarPos[-1] + visibleRouteLength*0.25, zStarPos[-1] + visibleRouteLength*0.25, '(Destination)', color='1', zorder=10, fontsize='small', horizontalalignment='center', verticalalignment='top')
	# LY
	for routeDistance in range(visibleRouteLength-1):
		if routeDistance > 8:
			break
		ax.text((xStarPos[routeDistance]+xStarPos[routeDistance+1])/2, (yStarPos[routeDistance]+yStarPos[routeDistance+1])/2, (zStarPos[routeDistance]+zStarPos[routeDistance+1])/2, round(math.sqrt((xStarPos[routeDistance+1]-(xStarPos[routeDistance]))**2+(yStarPos[routeDistance+1]-(yStarPos[routeDistance]))**2+(zStarPos[routeDistance+1]-(zStarPos[routeDistance]))**2), 1), color='1', zorder=10, fontsize='small', horizontalalignment='right', verticalalignment='center')
		ax.text((xStarPos[routeDistance]+xStarPos[routeDistance+1])/2, (yStarPos[routeDistance]+yStarPos[routeDistance+1])/2, (zStarPos[routeDistance]+zStarPos[routeDistance+1])/2, 'LY', color='1', zorder=10, fontsize='x-small', horizontalalignment='left', verticalalignment='center')

	# Set Visibility
	print(debugmodeNavRoute, ax.texts)
	for text in ax.texts:
		text.set_visible(True)

	##############################
	## Draw & Rotate Plot/Route ##
	##############################
	while True:
		rotateSpeed = 7
		angle = 0

		while angle < 1080: # Rotate 3x & Repeat
			# Pause Plot/Route Rotation
			while pauseRequested == True and navRoutePathModTime == os.stat(navRoutePath).st_mtime and refreshRequested == False:
				plt.pause(.1)
			
			############################
			## Watch for File Changes ##
			############################

			# Journal*.log Changes
			if journalPathModTime != os.stat(journalPath).st_mtime:
				# Files Changed
				print(debugmodeNavRoute, 'Journal File Changed in ModeNavRoute...' + str(journalPathModTime) + ' | ' + str(os.stat(journalPath).st_mtime))

				# Reimport journalData & process
				importedJournalData, journalPathModTime, journalPath = importEDDataJournal(edRootPath)
				processedJournalData, currentMode, minRequiredData = processEDDataJournal(importedJournalData, args.locale, args.shutdown)

				# Check if Mode Changed in Auto Mode
				if currentMode != 'ModeNavRoute':
					# Mode Changed Exit
					print(debugmodeNavRoute, 'Auto Mode Request Received in ModeNavRoute...')
					exitModeNavRoute = True
					break

				#############################################
				## Check for ED Data Updates & Update Text ##
				#############################################

				# Check for New Star System
				if currentSystem != processedJournalData['starSystem']:
					# Restart modeNavRoute for New Star System
					print(debugmodeNavRoute, 'Entering New Star System')
					#discovery.set_text('Discovery - | Bodies - | NonBodies -')
					restartModeNavRoute = True
					break
				
				# Check for Updates to Discovery Scanner
				if currentSystem == processedJournalData.get('fssdsSystemName', None):
					fssdsProgress = round(processedJournalData.get('fssdsProgress', 0)*100)
					if fssdsProgress == 0:
						fssdsProgress = '-'
					discovery.set_text('Discovery ' + str(fssdsProgress) + '%' + ' | ' + 'Bodies ' + str(processedJournalData.get('fssdsBodyCount', ' -')) + ' | ' + 'NonBodies ' + str(processedJournalData.get('fssdsNonBodyCount', ' -')))
				fleetcarriers.set_text('Fleet Carriers ' + str(len(list(dict.fromkeys(processedJournalData['fleetCarriers'])))))
			
			# Status.json Changes
			if statusPathModTime != os.stat(statusPath).st_mtime:
				# Files Changed
				print(debugmodeNavRoute, 'Status File Changed in ModeNavRoute...' + str(statusPathModTime) + ' | ' + str(os.stat(statusPath).st_mtime))

				# Reimport statusData & process
				importedStatusData, statusPathModTime, statusPath = importEDDataJSON('Status', edRootPath)
				processedStatusData = processEDDataStatus(importedStatusData)

				#############################################
				## Check for ED Data Updates & Update Text ##
				#############################################
				
				# Check for Updates to Fuel
				fuelBar, fuelPercent, fuelBarColor, fuelLevel, fuelCapacity = getFuel(processedJournalData, processedStatusData)
				fuel.set_text('Fuel ' + fuelLevel + '/' + fuelCapacity + ' T')
				fuel2dBar.set_text(fuelBar + ' ' + fuelPercent)
				fuel2dBar.set_color(fuelBarColor)

			# Check if Mode Changed to Manual Mode
			if manualModeRequest != None and manualModeRequest != 'ModeNavRoute':
				# Mode Changed & Exit
				print(debugmodeNavRoute, 'Manual Mode Request Received in ModeNavRoute...')
				exitModeNavRoute = True
				break

			# Watch NavRoute JSON for Changes
			if navRoutePathModTime != os.stat(navRoutePath).st_mtime or refreshRequested == True:
				# NavRoute JSON Changed & Exit
				print(debugmodeNavRoute, 'NavRoute File Changed in ModeNavRoute...' + str(navRoutePathModTime) + ' | ' + str(os.stat(navRoutePath).st_mtime))
				restartModeNavRoute = True
				pauseRequested = False
				break

			# Check for different/newer Journal*.log file
			newjournalPath = list(edRootPath.glob('Journal*.log'))[-1]
			if newjournalPath != journalPath:
				break
			
			# Set Angle & Draw
			ax.view_init(angle*.3, angle)
			plt.draw()
			plt.pause(.03)
			# Slowly Adjust Rotation Speed Down
			if rotateSpeed > .1:
				angle += rotateSpeed
				rotateSpeed *= 0.95
			else:
				angle += .1
		# Check for Restarts/Exits
		if restartModeNavRoute == True or exitModeNavRoute == True:
			break

def modeDocked():
	# Global Variables
	global currentMode
	global manualModeRequest

	# Initialize Variables
	debugmodeDocked = 'DOCKED:'
	currentMode = 'ModeDocked'

	# Find All Ship Modules
	if modulesData != None:
		slot, item, itemClass, itemRating, bluePrint, level, expEffect = getShipModules(processedJournalData, modulesData)
	else:
		slot = None
		item = None
		itemClass = None
		itemRating = None
		bluePrint = None
		level = None
		expEffect = None
	print(debugmodeDocked, slot, item, itemClass, itemRating, bluePrint, level, expEffect)

	# Find All System Stations
	stationServices, allStations = closestSystemServices(processedJournalData['starSystem'], systemsPopData, stationsData)
	print(debugmodeDocked, 'All Stations:', allStations, len(allStations))

	#############
	## 2D Text ##
	#############

	# Mode
	ax.text2D(0.99, 0.99, ('Docked/Stats Mode') , color='1', fontsize='large', fontweight='bold', horizontalalignment='right', transform=ax.transAxes)
	
	# Star System Info
	starSystemStartingX = 0.01
	starSystemStartingY = 0.99
	starSystemInc = 0.0175
	starSystemHeaderFontSize = 'large'
	starSystemFontSize = 'medium'
	ax.text2D(starSystemStartingX, starSystemStartingY, ('Star System - ') + processedJournalData.get('starSystem', '-'), color='1', fontsize=starSystemHeaderFontSize, fontweight='bold', horizontalalignment='left', transform=ax.transAxes); starSystemStartingY -= starSystemInc
	ax.text2D(starSystemStartingX, starSystemStartingY, ('Allegiance - ') + processedJournalData.get('systemAllegiance', '-'), color='1', fontsize=starSystemFontSize, horizontalalignment='left', transform=ax.transAxes); starSystemStartingY -= starSystemInc
	ax.text2D(starSystemStartingX, starSystemStartingY, ('Economy - ') + processedJournalData.get('systemEconomy', '-'), color='1', fontsize=starSystemFontSize, horizontalalignment='left', transform=ax.transAxes); starSystemStartingY -= starSystemInc
	ax.text2D(starSystemStartingX, starSystemStartingY, ('Sec. Economy - ') + processedJournalData.get('systemSecondEconomy', '-'), color='1', fontsize=starSystemFontSize, horizontalalignment='left', transform=ax.transAxes); starSystemStartingY -= starSystemInc
	ax.text2D(starSystemStartingX, starSystemStartingY, ('Government - ') + processedJournalData.get('systemGovernment', '-'), color='1', fontsize=starSystemFontSize, horizontalalignment='left', transform=ax.transAxes); starSystemStartingY -= starSystemInc
	ax.text2D(starSystemStartingX, starSystemStartingY, processedJournalData.get('systemSecurity', '-'), color='1', fontsize=starSystemFontSize, horizontalalignment='left', transform=ax.transAxes); starSystemStartingY -= starSystemInc
	ax.text2D(starSystemStartingX, starSystemStartingY, ('Population - ') + str(processedJournalData.get('systemPopulation', '-')), color='1', fontsize=starSystemFontSize, horizontalalignment='left', transform=ax.transAxes); starSystemStartingY -= starSystemInc

	# Station Info
	stationInfoStartingX = 0.35
	stationInfoStartingY = 0.99
	stationInfoInc = 0.0175
	stationInfoHeaderFontSize = 'large'
	stationInfoFontSize = 'medium'
	ax.text2D(stationInfoStartingX, stationInfoStartingY, ('Station - ') + processedJournalData.get('stationName', '-'), color='1', fontsize=stationInfoHeaderFontSize, fontweight='bold', horizontalalignment='left', transform=ax.transAxes); stationInfoStartingY -= stationInfoInc
	ax.text2D(stationInfoStartingX, stationInfoStartingY, ('Type - ') + processedJournalData.get('stationType', '-'), color='1', fontsize=stationInfoFontSize, horizontalalignment='left', transform=ax.transAxes); stationInfoStartingY -= stationInfoInc
	ax.text2D(stationInfoStartingX, stationInfoStartingY, ('Economy - ') + processedJournalData.get('stationEconomy', '-'), color='1', fontsize=stationInfoFontSize, horizontalalignment='left', transform=ax.transAxes); stationInfoStartingY -= stationInfoInc
	ax.text2D(stationInfoStartingX, stationInfoStartingY, ('Government - ') + processedJournalData.get('stationGovernment', '-'), color='1', fontsize=stationInfoFontSize, horizontalalignment='left', transform=ax.transAxes); stationInfoStartingY -= stationInfoInc
	ax.text2D(stationInfoStartingX, stationInfoStartingY, ('Distance - ') + str(processedJournalData.get('stationDistFromStarLS', '-')) + ' LS', color='1', fontsize=stationInfoFontSize, horizontalalignment='left', transform=ax.transAxes); stationInfoStartingY -= stationInfoInc
	ax.text2D(stationInfoStartingX, stationInfoStartingY, ('Landing Pads ') + processedJournalData.get('stationLandingPadsS', '-') + '|' + processedJournalData.get('stationLandingPadsM', '-') + '|' + processedJournalData.get('stationLandingPadsL', '-'), color='1', fontsize=stationInfoFontSize, horizontalalignment='left', transform=ax.transAxes); stationInfoStartingY -= stationInfoInc

	# Ranks
	ranksStartingX = 0.99
	ranksStaryingY = 0.97
	ranksInc = 0.0175
	rankFontSize = 'medium'
	ax.text2D(ranksStartingX, ranksStaryingY, ('Combat - ') + processedJournalData.get('rankCombat', '-'), color='1', fontsize=rankFontSize, horizontalalignment='right', transform=ax.transAxes); ranksStaryingY -= ranksInc
	ax.text2D(ranksStartingX, ranksStaryingY, ('Trade - ') + processedJournalData.get('rankTrade', '-'), color='1', fontsize=rankFontSize, horizontalalignment='right', transform=ax.transAxes); ranksStaryingY -= ranksInc
	ax.text2D(ranksStartingX, ranksStaryingY, ('Explore - ') + processedJournalData.get('rankExplore', '-'), color='1', fontsize=rankFontSize, horizontalalignment='right', transform=ax.transAxes); ranksStaryingY -= ranksInc
	ax.text2D(ranksStartingX, ranksStaryingY, ('Soldier - ') + processedJournalData.get('rankSoldier', '-'), color='1', fontsize=rankFontSize, horizontalalignment='right', transform=ax.transAxes); ranksStaryingY -= ranksInc
	ax.text2D(ranksStartingX, ranksStaryingY, ('Exobiologist - ') + processedJournalData.get('rankExobiologist', '-'), color='1', fontsize=rankFontSize, horizontalalignment='right', transform=ax.transAxes); ranksStaryingY -= ranksInc
	ax.text2D(ranksStartingX, ranksStaryingY, ('Empire - ') + processedJournalData.get('rankEmpire', '-'), color='1', fontsize=rankFontSize, horizontalalignment='right', transform=ax.transAxes); ranksStaryingY -= ranksInc
	ax.text2D(ranksStartingX, ranksStaryingY, ('Federation - ') + processedJournalData.get('rankFederation', '-'), color='1', fontsize=rankFontSize, horizontalalignment='right', transform=ax.transAxes); ranksStaryingY -= ranksInc
	ax.text2D(ranksStartingX, ranksStaryingY, ('CQC - ') + processedJournalData.get('rankCQC', '-'), color='1', fontsize=rankFontSize, horizontalalignment='right', transform=ax.transAxes); ranksStaryingY -= ranksInc

	# Show All Stations
	allStationsStartingX = 0.20
	allStationsStartingY = 0.60
	allStationsInc = 0.02
	allStationsFontSize = 'small'
	allStationsCount = 0
	allStationsMax = 30
	allStationsMaxNameLen = 25
	ax.text2D(allStationsStartingX, allStationsStartingY, processedJournalData.get('starSystem', '-'), color='1', fontsize='small', horizontalalignment='right', transform=ax.transAxes); allStationsStartingX += 0.013
	ax.text2D(allStationsStartingX, allStationsStartingY-0.004, str(u"✧"), color='yellow', fontsize='xx-large', fontweight='bold', horizontalalignment='center', transform=ax.transAxes); allStationsStartingX += 0.013
	for station in allStations:
		if station[1]['Name'] == processedJournalData['stationName']:
			if station[1]['Planetary'] == True:
				ax.text2D(allStationsStartingX, allStationsStartingY, str(u"◯ | ") + ((station[1]['Name'][:allStationsMaxNameLen] + '..') if len(station[1]['Name']) > allStationsMaxNameLen+2 else station[1]['Name']) + '\n', color='orange', fontsize=allStationsFontSize, fontweight='bold', horizontalalignment='left', rotation=90, transform=ax.transAxes); allStationsStartingX += allStationsInc
			elif station[1]['Planetary'] == False:
				ax.text2D(allStationsStartingX, allStationsStartingY, str(u"◻  | ") + ((station[1]['Name'][:allStationsMaxNameLen] + '..') if len(station[1]['Name']) > allStationsMaxNameLen+2 else station[1]['Name']) + '\n', color='orange', fontsize=allStationsFontSize, fontweight='bold', horizontalalignment='left', rotation=90, transform=ax.transAxes); allStationsStartingX += allStationsInc
			else:
				pass
		else:
			if station[1]['Planetary'] == True:
				ax.text2D(allStationsStartingX, allStationsStartingY, str(u"◯ | ") + ((station[1]['Name'][:allStationsMaxNameLen] + '..') if len(station[1]['Name']) > allStationsMaxNameLen+2 else station[1]['Name']) + '\n', color='grey', fontsize=allStationsFontSize, fontweight='bold', horizontalalignment='left', rotation=90, transform=ax.transAxes); allStationsStartingX += allStationsInc
			elif station[1]['Planetary'] == False:
				ax.text2D(allStationsStartingX, allStationsStartingY, str(u"◻  | ") + ((station[1]['Name'][:allStationsMaxNameLen] + '..') if len(station[1]['Name']) > allStationsMaxNameLen+2 else station[1]['Name']) + '\n', color='1', fontsize=allStationsFontSize, fontweight='bold', horizontalalignment='left', rotation=90, transform=ax.transAxes); allStationsStartingX += allStationsInc
			else:
				pass
		allStationsCount+=1
		if allStationsCount > allStationsMax:
			ax.text2D(allStationsStartingX, allStationsStartingY, '...', color='grey', fontsize='medium', fontweight='bold', horizontalalignment='left', transform=ax.transAxes); allStationsStartingX += allStationsInc
			break

	# Credits & Commander Info
	creditCommanderStartingX = 0.99
	creditCommanderStaryingY = 0.53
	creditCommanderInc = 0.0175
	creditCommanderFontSize = 'large'
	ax.text2D(creditCommanderStartingX, creditCommanderStaryingY, ('Credits ') + locale.format_string('%d', processedStatusData.get('credits', '-'), grouping=True), color='1', fontsize=creditCommanderFontSize, horizontalalignment='right', transform=ax.transAxes); creditCommanderStaryingY -= creditCommanderInc
	ax.text2D(creditCommanderStartingX, creditCommanderStaryingY, ('CMDR ') + processedJournalData.get('cmdrName', '-'), color='1', fontsize=creditCommanderFontSize, horizontalalignment='right', transform=ax.transAxes); creditCommanderStaryingY -= creditCommanderInc

	# Ship Info
	shipInfoStartingX = 0.01
	shipInfoStartingY = 0.53
	shipInfoInc = 0.0175
	shipInfoTextSize = 'large'
	ax.text2D(shipInfoStartingX, shipInfoStartingY, str(processedJournalData.get('ship', '-').title()) + ' ' + str(processedJournalData.get('shipName', '')) + ' ' + str(processedJournalData.get('shipIdent', '')), color='1', fontsize=shipInfoTextSize, fontweight='bold', horizontalalignment='left', transform=ax.transAxes); shipInfoStartingY -= shipInfoInc
	ax.text2D(shipInfoStartingX, shipInfoStartingY, ('  Value ') + processedJournalData.get('shipValue', '-'), color='lime', fontsize='medium', horizontalalignment='left', transform=ax.transAxes); shipInfoStartingY -= shipInfoInc
	ax.text2D(shipInfoStartingX, shipInfoStartingY, ('  Rebuy ') + processedJournalData.get('rebuy', '-'), color='lime', fontsize='medium', horizontalalignment='left', transform=ax.transAxes); shipInfoStartingY -= shipInfoInc
	ax.text2D(shipInfoStartingX, shipInfoStartingY, ('Max Jump Range - ') + processedJournalData.get('maxJumpRange', '-') + ' LY', color='1', fontsize=shipInfoTextSize, horizontalalignment='left', transform=ax.transAxes); shipInfoStartingY -= shipInfoInc
	ax.text2D(shipInfoStartingX, shipInfoStartingY, ('Fuel - ') + str(processedStatusData.get('fuelLevel', '-')) + ' / ' + str(processedJournalData.get('fuelCapacity', '-')) + ' T', color='1', fontsize=shipInfoTextSize, horizontalalignment='left', transform=ax.transAxes); shipInfoStartingY -= shipInfoInc
	ax.text2D(shipInfoStartingX, shipInfoStartingY, ('Unladen Mass - ') + str(processedJournalData.get('shipUnladenMass', '-')) + ' T', color='1', fontsize=shipInfoTextSize, horizontalalignment='left', transform=ax.transAxes); shipInfoStartingY -= shipInfoInc
	ax.text2D(shipInfoStartingX, shipInfoStartingY, ('Cargo - ') + processedJournalData.get('currentCargo', '-') + ' / ' + processedJournalData.get('cargoCapacity', '-'), color='1', fontsize=shipInfoTextSize, horizontalalignment='left', transform=ax.transAxes); shipInfoStartingY -= shipInfoInc
	#shipInfoStartingY -= shipInfoInc

	# Cargo/Inventory
	#ax.text2D(shipInfoStartingX, shipInfoStartingY, ('[Inventory]'), color='1', fontsize='medium', horizontalalignment='left', transform=ax.transAxes); shipInfoStartingY -= shipInfoInc
	#ax.text2D(shipInfoStartingX, shipInfoStartingY, str(processedJournalData.get('currentInventory', '')), color='1', fontsize='medium', horizontalalignment='left', transform=ax.transAxes); shipInfoStartingY -= shipInfoInc
	#print(processedJournalData['currentInventory'])
	
	# Module Info
	moduleBaseX = 0.01
	moduleBaseY = 0.37
	moduleStartingX = moduleBaseX
	moduleStartingY = moduleBaseY
	moduleXInc = 0.30
	moduleYInc = 0.0175
	moduleTextSize = 'medium'
	moduleEngTextSize = 'small'
	if modulesData != None:
		ax.text2D(moduleStartingX, moduleStartingY, ('[Modules]'), color='1', fontsize=moduleTextSize, horizontalalignment='left', transform=ax.transAxes); moduleStartingY -= shipInfoInc
		for singleSlot in range(len(slot)):
			if item[singleSlot] == None:
				continue
			if slot[singleSlot] == 'Armour':
				moduleStartingX += moduleXInc
				moduleStartingY = moduleBaseY
			ax.text2D(moduleStartingX, moduleStartingY, str(itemClass[singleSlot]) + str(itemRating[singleSlot]) + ' ' + str(item[singleSlot]), color='1', fontsize=moduleTextSize, horizontalalignment='left', transform=ax.transAxes)
			# Engineering
			if bluePrint[singleSlot] != None and level[singleSlot] != None:
				moduleStartingY -= moduleYInc
				ax.text2D(moduleStartingX, moduleStartingY, '  ' + str(bluePrint[singleSlot] if bluePrint[singleSlot] != None else '') + ' | Level ' + str(level[singleSlot] if level[singleSlot] != None else ''), color='orange', fontsize=moduleEngTextSize, horizontalalignment='left', transform=ax.transAxes)
			# Experimental Effects
			if expEffect[singleSlot] != None:
				moduleStartingY -= moduleYInc
				ax.text2D(moduleStartingX, moduleStartingY, '  ' + str(expEffect[singleSlot] if expEffect[singleSlot] != None else ''), color='orange', fontsize=moduleEngTextSize, horizontalalignment='left', transform=ax.transAxes)
			if slot[singleSlot] == 'FuelTank':
				moduleStartingX += moduleXInc
				moduleStartingY = moduleBaseY
				continue
			moduleStartingY -= moduleYInc

	# Set Visibility
	print(debugmodeDocked, ax.texts)
	for text in ax.texts:
		text.set_visible(True)
	
	######################
	## Draw Docked Info ##
	######################
	while True:
		# Watch for File Changes
		if journalPathModTime != os.stat(journalPath).st_mtime or statusPathModTime != os.stat(statusPath).st_mtime:
			# Files Changed
			print(debugmodeDocked, 'Files Changed in ModeDocked...')
			break
		
		# Check if Mode Changed to Manual Mode
		if manualModeRequest != None and manualModeRequest != 'ModeDocked':
			# Mode Changed Exit
			print(debugmodeDocked, 'Manual Mode Request Received in ModeDocked...')
			break

		# Check for different/newer Journal*.log file
		newjournalPath = list(edRootPath.glob('Journal*.log'))[-1]
		if newjournalPath != journalPath:
			break

		# Draw
		plt.draw()
		plt.pause(.5)

fig = pltFigure()

# Start in Auto Mode by default
manualModeRequest = args.mode

# Initialize Variables
debugMain = 'MAIN:'

# Elite Dangerous Path
edRootPath = Path(os.environ['USERPROFILE'] + '/Saved Games/Frontier Developments/Elite Dangerous/')

# Import EDDB.io data
systemsPopData = importEDDBIOData('systems_populated.json', edRootPath)
stationsData = importEDDBIOData('stations.json', edRootPath)
modulesData = importEDDBIOData('modules.json', edRootPath)

# Main Loop
while True:
	# Import Data
	minRequiredData = False
	while minRequiredData == False:
		# Wait For All Required Data
		importedJournalData, journalPathModTime, journalPath = importEDDataJournal(edRootPath) # Read Journal*.log
		importedStatusData, statusPathModTime, statusPath = importEDDataJSON('Status', edRootPath) # Read Status.json
		importedNavRouteData, navRoutePathModTime, navRoutePath = importEDDataJSON('NavRoute', edRootPath) # Read NavRoute.json
		processedStatusData = processEDDataStatus(importedStatusData) # Process Status.json
		processedJournalData, currentMode, minRequiredData = processEDDataJournal(importedJournalData, args.locale, args.shutdown) # Process Journal*.log
		if minRequiredData == False:
			time.sleep(1)

	# Check Auto/Manual Mode
	if manualModeRequest == None:
		pass # Auto Mode
	else:
		currentMode = manualModeRequest # Manual Mode
	
	print(debugMain, 'Current Mode: ' + currentMode)

	# Clear Figure
	ax = pltAxes()
	
	# Switch Mode
	if currentMode == 'ModeNavRoute':
		modeNavRoute(processedJournalData, journalPathModTime, journalPath, processedStatusData, statusPathModTime, statusPath)
	elif currentMode == 'ModeDocked':
		modeDocked()
	else:
		print('UNKNOWN: Unknown mode requested')
		quit()