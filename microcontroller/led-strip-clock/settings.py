from ujson import loads, dumps

settings = {"netId": "0", "essid": "", "group": "", "color": "0000ff"}


def createSettings():
    global settings

    file = open("settings.json", "w")
    file.write(dumps(settings))
    file.close


def readSettings():
    global settings

    try:
        file = open("settings.json", "r")
        jsonSettings = file.read()
        file.close

        settings = loads(jsonSettings)
    except:
        createSettings()

    return settings


def writeSettings():
    file = open("settings.json", "w")

    file.write(dumps(settings))
    file.close()


def readEssid():
    readSettings()
    return settings["essid"]


def writeEssid(essid):
    global settings

    readSettings()
    settings["essid"] = essid
    writeSettings()


def readNetId():
    readSettings()
    return settings["netId"]


def writeNetId(netId):
    global settings

    readSettings()
    settings["netId"] = netId
    writeSettings()


def readGroup():
    readSettings()
    return settings["group"]


def writeGroup(group):
    global settings

    readSettings()
    settings["group"] = group
    writeSettings()


def readColor():
    readSettings()
    return settings["color"]


def writeColor(color):
    global settings

    readSettings()
    settings["color"] = color
    writeSettings()
