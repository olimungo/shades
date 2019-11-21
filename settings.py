def createSettings():
    content = "0,Unknown,0"
    file = open("settings.txt", "w")
    file.write(content)
    file.close

    return content


def readSettings():
    try:
        file = open("settings.txt", "r")
        content = file.read()
        file.close
    except:
        content = createSettings()

    return content.split(",")


def writeSettings(netId, essid, motorReversed):
    file = open("settings.txt", "w")

    file.write(netId + "," + essid + "," + motorReversed)

    file.close()


def readEssid():
    netId, essid, motorReversed = readSettings()
    return essid


def writeEssid(essid):
    netId, x, motorReversed = readSettings()
    writeSettings(netId, essid, motorReversed)


def readNetId():
    netId, essid, motorReversed = readSettings()
    return netId


def writeNetId(netId):
    x, essid, motorReversed = readSettings()
    writeSettings(netId, essid, motorReversed)


def readMotorReversed():
    netId, essid, motorReversed = readSettings()
    return motorReversed


def writeMotorReversed():
    netId, essid, motorReversed = readSettings()

    if motorReversed == "0":
        motorReversed = "1"
    else:
        motorReversed = "0"

    writeSettings(netId, essid, motorReversed)
