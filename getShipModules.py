# Find All Ship Modules
def getShipModules(processedJournalData, modulesData):
	# Initialize Variables
    slot = []
    item = []
    itemClass = []
    itemRating = []
    bluePrint = []
    level = []
    expEffect = []
    for module in processedJournalData['modules']:
        slot.append(module['Slot'])
        itemFound = False
        for eddbModule in modulesData:
            if eddbModule['ed_symbol'].lower() == module['Item']:
                itemFound = True
                item.append(eddbModule['group']['name'])
                itemClass.append(eddbModule['class'])
                itemRating.append(eddbModule['rating'])
        if itemFound == False:
            item.append(None)
            itemClass.append(None)
            itemRating.append(None)
        engineering = module.get('Engineering', None)
        if engineering != None:
            bluePrint.append(module['Engineering']['BlueprintName'])
            level.append(module['Engineering']['Level'])
            try:
                expEffect.append(module['Engineering']['ExperimentalEffect_Localised'])
            except:
                expEffect.append(None)
        else:
            bluePrint.append(None)
            level.append(None)
            expEffect.append(None)
    return slot, item, itemClass, itemRating, bluePrint, level, expEffect