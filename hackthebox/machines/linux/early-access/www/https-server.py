#!/bin/env python
import http.server, ssl

httpd = http.server.HTTPServer(
    ('10.10.16.2', 4343),
    http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(
    httpd.socket,
    server_side=True,
    certfile='localhost.pem',
    ssl_version=ssl.PROTOCOL_TLS)
httpd.serve_forever()
