import os
import sys
import subprocess
import webbrowser
import time
import socket

def install_dependencies():
    print("Checking dependencies...")
    try:
        import flask
        import flask_cors
        print("Dependencies found.")
    except ImportError:
        print("Dependencies missing. Installing from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Installation complete.")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_backend():
    print("Starting AI Assistant Backend...")
    # Start the flask app in a way that doesn't block the script if we want to open browser
    # But usually, it's easier to start the app last or in a thread.
    # Here we'll start it and then open the browser after a short delay.
    
    port = 5000
    if is_port_in_use(port):
        print(f"Warning: Port {port} is already in use. Attempting to start anyway...")

    print(f"Server will be available at http://localhost:{port}")
    
    # Open browser in a separate thread/delay
    def open_browser():
        time.sleep(2)
        print("Opening browser...")
        webbrowser.open(f"http://localhost:{port}")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run the app
    try:
        from app import app
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Critical Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    print("========================================")
    print("   AI ASSISTANT STARTUP MANAGER")
    print("========================================")
    
    # Ensure current directory is the project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    install_dependencies()
    start_backend()
