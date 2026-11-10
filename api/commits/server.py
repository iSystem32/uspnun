import http.server
import socketserver
import subprocess
import json
import os

PORT = 8080

# Cambiar al directorio del script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class GitHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Si piden la ruta /api/commits, devolvemos el historial de git en formato JSON
        if self.path == '/api/commits':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
            try:
                # Ejecutamos git log para obtener hash, autor, fecha y mensaje
                cmd = ['git', 'log', '-n', '10', '--format={"hash": "%h", "author": "%an", "date": "%ar", "message": "%s"}']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                # Formateamos la salida como un array JSON válido
                commits_lines = result.stdout.strip().split('\n')
                commits_json = "[" + ",".join([line for line in commits_lines if line]) + "]"
                
                self.wfile.write(commits_json.encode('utf-8'))
            except Exception as e:
                error_msg = json.dumps([{"hash": "error", "author": "Sistema", "date": "ahora", "message": f"No se pudo leer Git: {str(e)}"}])
                self.wfile.write(error_msg.encode('utf-8'))
            return
        
        # Para cualquier otro archivo (index.html, imagenes, etc.), usamos el comportamiento normal
        super().do_GET()

with socketserver.TCPServer(("", PORT), GitHandler) as httpd:
    print(f"Servidor Activo en: http://localhost:{PORT}")
    print("Leyendo commits directamente del repositorio Git local...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")