# Class which runs a simple http server in process -- to use for testing
from __future__ import absolute_import, division, print_function
import BaseHTTPServer as server  # on py3: http.server as ...
from SocketServer import TCPServer
from multiprocessing import Process, Queue
from sys import stderr


class MyHTTPD:

    class MyHTTPHandler(server.BaseHTTPRequestHandler):
        def do_GET(self):
            if "favicon.ico" in self.path.lower():
                self.send_response(404)
                return

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            headers = self.headers.dict.copy()  # copy for outside
            headers["PATH"] = self.path
            self.server.queue.put(headers)

            html = self.server.html_to_serve \
                if self.server.html_to_serve \
                else "<html>%s</html>" % self.headers
            self.wfile.write(html.encode())

    def __init__(self, bind_port, bind_ip="127.0.0.1", html_to_serve=None):
        self.queue = Queue()
        self.server = TCPServer((bind_ip, bind_port), MyHTTPD.MyHTTPHandler)
        print("DEBUG: MyHTTPD serving on http://%s:%d" % (bind_ip, bind_port))
        self.server.queue = self.queue
        self.server.html_to_serve = html_to_serve
        # Process advised over threading for python/multi-core
        self.process = Process(target=self.server.serve_forever)
        self.process.daemon = True
        self.process.start()

    def get_seen_header(self, timeout=None):
        return self.queue.get(timeout=timeout)  # cool: blocks if queue empty!

    def shutdown(self):
        # unsure why but self.server.shutdown() didnt' work -- but this works ok:
        self.process.terminate()

    def __del__(self):
        self.shutdown()
