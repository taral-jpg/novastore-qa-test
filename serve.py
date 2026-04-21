# serve.py
import http.server
import socketserver
import os

PORT = 8000
handler = http.server.SimpleHTTPRequestHandler

# Ensure it serves novastore-qa.html as the index
class MyHandler(handler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/novastore-qa.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    # Change directory to the script's directory to serve files correctly
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            httpd.server_close()
