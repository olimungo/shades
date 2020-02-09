import usocket as socket
import uselect
import ure


class WebServer:
    webServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    poller = uselect.poll()

    def __init__(self):
        self.webServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.webServer.bind(("", 80))
        self.webServer.listen(1)

        self.poller.register(self.webServer, uselect.POLLIN)

    def ok(self, client):
        print("> Send empty OK response")

        client.send("HTTP/1.1 200 OK")
        client.close()

    def notFound(self, client):
        print("> Send Page not found")

        client.send(
            "HTTP/1.1 404 Not Found\r\n\r\nQUOD GRATIS ASSERITUR, GRATIS NEGATUR"
        )
        client.close()

    def index(self, client, ip, netId, essid, motorReversed, group):
        print("> Send index page")

        file = open("index.html", "r")

        while True:
            data = file.readline()

            if data == "":
                break

            data = data.replace("%%IP%%", ip)
            data = data.replace("%%NET_ID%%", netId)
            data = data.replace("%%ESSID%%", essid)
            data = data.replace("%%GROUP%%", group)

            if motorReversed == "1":
                checked = "CHECKED"
            else:
                checked = ""

            data = data.replace("%%MOTOR_REVERSED%%", checked)

            client.write(data)

        file.close()

        client.close()

    def splitRequest(self, request):
        path = ""
        queryStrings = {}
        queryStringsArray = {}

        try:
            regex = ure.compile("[\r\n]")
            firstLine = str(regex.split(request)[0])
            _, url, _ = firstLine.split(" ")

            path = url

            if len(url.split("?")) == 2:
                path, queryString = url.split("?")
                queryStrings = queryString.split("&")

            for item in queryStrings:
                k, v = item.split("=")
                queryStringsArray[k] = v
        except:
            print("> Bad request: " + request)

        return path, queryStringsArray

    def handleRequest(self):
        request = self.poller.poll(1)

        if request:
            client, addr = self.webServer.accept()
            request = client.recv(4096)
            path, queryStringsArray = self.splitRequest(request)

            return False, client, path, queryStringsArray
        else:
            return True, False, False, False
