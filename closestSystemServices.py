# Find Closest System Services
def closestSystemServices(selectedSystem, systemsPopData, stationsData):
    if systemsPopData != None and stationsData != None:
        currentSystemID = None
        for systemPopData in systemsPopData:
            if systemPopData['name'] == selectedSystem:
                currentSystemID = systemPopData['id']

        stationServices = {'has_refuel':None, 'has_repair':None, 'has_rearm':None, 'has_outfitting':None, 'has_shipyard':None, 'has_material_trader':None, 'has_technology_broker':None}

        for stationData in stationsData:
            for stationService in stationServices:
                if stationData['system_id'] == currentSystemID and \
                stationData[stationService] == True and \
                stationData['type'] != 'Fleet Carrier' and \
                stationData['is_planetary'] == False and \
                (stationServices[stationService] == None or stationData['distance_to_star'] < stationServices[stationService]['Distance (LS)']):
                    stationServices[stationService] = {\
                        'Name':stationData['name'], \
                        'Distance (LS)':stationData['distance_to_star'], \
                        'Landing Pad':stationData['max_landing_pad_size'], \
                        'Fuel':'Fuel' if stationData['has_refuel'] else '', \
                        'Repair':'Repair' if stationData['has_repair'] else '', \
                        'Rearm':'Rearm' if stationData['has_rearm'] else '', \
                        'Outfitting':'Outfitting' if stationData['has_outfitting'] else '', \
                        'Shipyard':'Shipyard' if stationData['has_shipyard'] else '', \
                        'Material Trader':'Material Trader' if stationData['has_material_trader'] else '', \
                        'Tech Broker':'Tech Broker' if stationData['has_technology_broker'] else ''}
        return stationServices, currentSystemID
    else:
        stationServices = None
        currentSystemID = None
        systemPopData = None
        return stationServices, currentSystemID