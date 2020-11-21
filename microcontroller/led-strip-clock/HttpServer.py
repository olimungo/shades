from usocket import socket, getaddrinfo, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from uselect import poll, POLLIN
from ure import compile
from gc import collect, mem_free

from UdpServer import UdpServer

MAX_PACKET_SIZE = const(1024)
HTTP_PORT = const(80)


class HttpServer:
    def __init__(self, ip, routes):
        self.ip = ip
        self.routes = routes

        self.udp = UdpServer(self.ip)

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        addr = getaddrinfo(self.ip, HTTP_PORT)[0][-1]
        self.sock.bind(addr)
        self.sock.listen(1)
        
        self.poller = poll()
        self.poller.register(self.sock, POLLIN)

    def _splitRequest(self, request):
        path = ""
        queryStrings = {}
        queryStringsArray = {}

        try:
            regex = compile("[\r\n]")
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

    def ok(self, client):
        print("> Send empty OK response")

        client.send("HTTP/1.1 200 OK\r\n\r\n")
        client.close()

    def notFound(self, client):
        print("> Send Page not found")

        client.send(
            "HTTP/1.1 404 Not Found\r\n\r\nQUOD GRATIS ASSERITUR, GRATIS NEGATUR\r\n\r\n"
        )
        client.close()

    def redirectToIndex(self, client):
        print("> Send 302 Redirect")
        client.send("HTTP/1.1 302 Redirect\r\nLocation: index.html\r\n\r\n")
        client.close()

    def index(self, client, interpolate):
        print("> Send index page")

        file = open("index.html", "rb")

        while True:
            data = file.readline()

            if data == b"":
                break

            if data != b"\n":
                client.write(data)

        file.close()

        client.close()

    def poll(self):
        request = self.poller.poll(1)

        if request:
            client, addr = self.sock.accept()

            collect()

            try:
                request = client.recv(MAX_PACKET_SIZE)

                path, queryStringsArray = self._splitRequest(request)

                del request
                collect()
            except Exception as e:
                print("> WebServer.poll exception: {}".format(e))
                print("> Mem free at the moment of the error: {}".format(mem_free()))
                return True, False, False, False

            return False, client, path, queryStringsArray
        else:
            return True, False, False, False
