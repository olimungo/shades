settings = []


def createSettings():
    global settings

    settingsString = "0,,0"
    file = open("settings.txt", "w")
    file.write(settingsString)
    file.close

    settings = settingsString.split(",")


def readSettings():
    global settings

    if len(settings) == 0:
        try:
            file = open("settings.txt", "r")
            settingsString = file.read()
            file.close

            settings = settingsString.split(",")
        except:
            createSettings()

    return settings


def writeSettings(netId, essid, group):
    global settings

    file = open("settings.txt", "w")
    settingsString = netId + "," + essid + "," + group
    settings = settingsString.split(",")

    file.write(settingsString)
    file.close()


def readEssid():
    _, essid, _ = readSettings()
    return essid


def writeEssid(essid):
    netId, _, group = readSettings()
    writeSettings(netId, essid, group)


def readNetId():
    netId, _, _ = readSettings()
    return netId


def writeNetId(netId):
    _, essid, group = readSettings()
    writeSettings(netId, essid, group)


def readGroup():
    _, _, group = readSettings()
    return group


def writeGroup(group):
    netId, essid, _ = readSettings()
    writeSettings(netId, essid, group)
