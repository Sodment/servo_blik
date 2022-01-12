import http.server
import socketserver

from requests.sessions import HTTPAdapter

PORT = 8080

#Stworzenie klasy serwera dziediczacej po bazowym serwerze
class MyServer(http.server.BaseHTTPRequestHandler):
    def __init__(self, request: bytes, client_address: tuple[str, int], server: socketserver.BaseServer) -> None:
        super().__init__(request, client_address, server)

    #ustawienie odpowiedzi na GET
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open("store.json", 'r') as f:
            self.wfile.write(bytes(f.read().encode('utf-8'))) #odczytanie danych z pliku json

    #ustawienie odpowiedzi na POST
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])  #pobranie dlugosci danych
        post_data = self.rfile.read(content_length)  # pobranie samych danych
        with open("store.json", 'w') as f:
            f.write(post_data.decode('utf-8')) # zapisanie danych w pliku json
        self.wfile.write(post_data)


# uruchomienie serwera
with socketserver.TCPServer(("0.0.0.0", PORT), MyServer) as httpd:
    print("serving at 0.0.0.0:{}".format(PORT))
    httpd.serve_forever()