from usocket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from uselect import poll, POLLIN
from ure import compile
from gc import collect

from UdpServer import UdpServer

MAX_PACKET_SIZE = const(1024)
HTTP_PORT = const(80)

HEADER_OK = b"HTTP/1.1 200 OK\r\n\r\n"
REDIRECT = b"HTTP/1.1 302 Found\r\nLocation: index.html\r\n\r\n"
NO_CONTENT = b"HTTP/1.1 204 No Content\r\n\r\n"
CONTENT_TYPE = b"Content-Type: application/json\r\nContent-Length: %s\r\n\r\n%s"

class HttpServer:
    def __init__(self, routes):
        self.routes = routes

        self.udp = UdpServer()

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(("", HTTP_PORT))
        self.sock.listen(1)
        
        self.poller = poll()
        self.poller.register(self.sock, POLLIN)

    def split_request(self, request):
        method = ""
        path = ""
        queryStrings = {}
        params = {}

        if isinstance(request, bytes):
            request = request.decode('ascii')

        try:
            regex = compile("[\r\n]")
            request_per_line = regex.split(request)
            firstLine = str(request_per_line[0])
            method, url, _ = firstLine.split(" ")


            path = url

            if len(url.split("?")) == 2:
                path, queryString = url.split("?")
                queryStrings = queryString.split("&")

            for item in queryStrings:
                k, v = item.split("=")
                params[k] = v
        except:
            print("> Bad request: " + request)

        return method, path, params

    def redirect(self, client):
        print("> Send 302 Redirect")

        client.send(REDIRECT)
        client.close()

    def no_content(self, client):
        print("> Send 204 No Content")

        client.send(NO_CONTENT)
        client.close()

    def send_page(self, client, page):
        print("> Send page {}".format(page.decode('ascii')))

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

            polled_request = self.poller.poll(1)

            if polled_request:
                client, _ = self.sock.accept()
                request = client.recv(MAX_PACKET_SIZE)

                if request:
                    method, path, params = self.split_request(request)

                    print("REQ Method: {} | path: {}: params: {}".format(method, path, params))

                    route = self.routes.get(path.encode('ascii'), None)

                    if type(route) is bytes:
                        # Expect a filename, so return content of file
                        self.send_page(client, route)
                    elif callable(route):
                        self.call_route(client, route, params)
                    else:
                        self.no_content(client)
        except Exception as e:
            print("> HttpServer.handle exception: {}".format(e))
