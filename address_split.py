from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from mediator import Mediate

hostName='localhost'
hostPort=8080
class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        m=Mediate()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        print(self.path[:])
        request=str(self.path[3:-1])
        m.stay_to_mediate(request)
        self.wfile.write(bytes("<html><head><link rel=”icon” href=”data:,”/><title>Title goes here.</title></head>", "utf-8"))
        self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
        self.wfile.write(bytes("<p>Drone is not connected %s</p>" %self.path[:], "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        return

myServer = HTTPServer((hostName, hostPort), GetHandler)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))