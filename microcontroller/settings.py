settings = []


def createSettings():
    global settings

    settingsString = "0,Unknown,0,"
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


def writeSettings(netId, essid, motorReversed, group):
    global settings

    file = open("settings.txt", "w")
    settingsString = netId + "," + essid + "," + motorReversed + "," + group
    settings = settingsString.split(",")

    file.write(settingsString)
    file.close()


def readEssid():
    _, essid, _, _ = readSettings()
    return essid


def writeEssid(essid):
    netId, _, motorReversed, group = readSettings()
    writeSettings(netId, essid, motorReversed, group)


def readNetId():
    netId, _, _, _ = readSettings()
    return netId


def writeNetId(netId):
    _, essid, motorReversed, group = readSettings()
    writeSettings(netId, essid, motorReversed, group)


def readGroup():
    _, _, _, group = readSettings()
    return group


def writeGroup(group):
    netId, essid, motorReversed, _ = readSettings()
    writeSettings(netId, essid, motorReversed, group)


def readMotorReversed():
    _, _, motorReversed, _ = readSettings()
    return motorReversed


def writeMotorReversed():
    netId, essid, motorReversed, group = readSettings()

    if motorReversed == "0":
        motorReversed = "1"
    else:
        motorReversed = "0"

    writeSettings(netId, essid, motorReversed, group)
