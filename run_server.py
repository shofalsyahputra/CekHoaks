import os
import sys
import threading
import webbrowser

# Entry point cepat untuk menjalankan server backend dan aplikasi mobile web
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(current_dir, "backend")
    sys.path.insert(0, backend_dir)
    
    from api.server import run_server
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

    # Buka browser otomatis dalam 1 detik setelah server siap
    threading.Timer(1.2, lambda: webbrowser.open(f"http://localhost:{port}")).start()

    run_server(port)

