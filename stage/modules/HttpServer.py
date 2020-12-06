from usocket import socket, getaddrinfo, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from uselect import poll, POLLIN
from ure import compile
from gc import collect
from UdpServer import UdpServer

MAX_PACKET_SIZE = const(1024)
HTTP_PORT = const(80)

HEADER_OK = b"HTTP/1.1 200 OK\r\n\r\n"
REDIRECT = b"HTTP/1.1 302 Redirect\r\nLocation: index.html\r\n\r\n"
CONTENT_TYPE = b"Content-Type: application/json\r\nContent-Length: %s\r\n\r\n%s"

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

    def split_request(self, request):
        path = ""
        queryStrings = {}
        params = {}

        try:
            regex = compile("[\r\n]")
            request_per_line = regex.split(request)
            firstLine = str(request_per_line[0])
            _, url, _ = firstLine.split(" ")

            path = url

            if len(url.split("?")) == 2:
                path, queryString = url.split("?")
                queryStrings = queryString.split("&")

            for item in queryStrings:
                k, v = item.split("=")
                params[k] = v
        except:
            print("> Bad request: " + request)

        return path, params

    def redirect(self, client):
        print("> Send redirect")

        client.send(REDIRECT)
        client.close()

    def send_page(self, client, page):
        print("> Send page {}".format(page))

        file = open(page, "rb")

        while True:
            data = file.readline()

            if data == b"":
                break

            if data != b"\n":
                client.write(data)

        file.close()
        client.close()

    def call_route(self, client, route, params):
        # Call a function, which may or may not return a response
        response = route(params)
        
        body = response[0] or b""
        response = (response[1] or HEADER_OK) + CONTENT_TYPE % (len(body), body)

        client.send(response)
        client.close()

    def handle(self):
        try:
            collect()
            
            request = self.poller.poll(1)

            if request:
                client, addr = self.sock.accept()

                request = client.recv(MAX_PACKET_SIZE)

                if request:
                    path, params = self.split_request(request)

                    print("request: {}".format(request))

                    route = self.routes.get(path.encode('ascii'), None)

                    if type(route) is bytes:
                        # Expect a filename, so return contents of file
                        self.send_page(client, route)
                    elif callable(route):
                        self.call_route(client, route, params)
                    else:
                        self.redirect(client)
        except Exception as e:
            print("> HttpServer.handle exception: {}".format(e))
