import os
import json
import webbrowser
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading

app = Flask(__name__, static_folder='static')
CORS(app)

SECURITY_FILE = 'security.json'

def get_pin():
    if os.path.exists(SECURITY_FILE):
        with open(SECURITY_FILE, 'r') as f:
            data = json.load(f)
            # Support legacy 'password' key during migration
            return str(data.get('pin', data.get('password', '1234')))
    return '1234'

def set_pin(new_pin):
    with open(SECURITY_FILE, 'w') as f:
        json.dump({'pin': str(new_pin)}, f)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # Check both 'pin' and 'masterKey' for frontend compatibility
    input_pin = data.get('pin') or data.get('masterKey')
    if str(input_pin) == get_pin():
        return jsonify({'status': 'success'})
    return jsonify({'status': 'fail', 'message': 'Incorrect PIN'}), 401

@app.route('/api/change_pin', methods=['POST'])
def change_pin():
    data = request.json
    old_pin = data.get('old_pin')
    new_pin = data.get('new_pin')
    if str(old_pin) == get_pin():
        set_pin(new_pin)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'fail', 'message': 'Incorrect old PIN'}), 401

@app.route('/api/command', methods=['POST'])
def process_command():
    data = request.json
    command = data.get('command', '').lower().strip()
    
    response_msg = f"Command '{command}' recognized, but no matching action found."
    
    try:
        if "close application" in command or "exit application" in command:
            response_msg = "Closing application."
            def kill():
                os._exit(0)
            threading.Timer(1.0, kill).start()

        elif "switch off pc" in command or "switch off the pc" in command or "shutdown pc" in command:
            response_msg = "Shutting down the PC in 60 seconds. Say 'abort shutdown' to cancel."
            os.system("shutdown /s /t 60")

        elif "abort shutdown" in command:
            response_msg = "Shutdown aborted."
            os.system("shutdown /a")

        elif "lock portal" in command or "lock application" in command or "logout" in command:
            response_msg = "LOCK_PORTAL_TRIGGER" # Frontend will handle this specific string
            
        elif "change pin" in command or "update pin" in command:
            response_msg = "CHANGE_PIN_TRIGGER" # Frontend will handle this specific string

        elif "gmail" in command:
            response_msg = "Opening Gmail."
            webbrowser.open("https://mail.google.com")

        elif "chat gpt" in command or "chatgpt" in command:
            match = re.search(r'(?:search|ask|open)\s+(.*?)\s+(?:on|in|directly on)\s+(?:chat gpt|chatgpt)', command)
            if match:
                query = match.group(1).strip()
                response_msg = f"Asking ChatGPT: {query}"
                webbrowser.open(f"https://chatgpt.com/?q={query}")
            else:
                response_msg = "Opening ChatGPT."
                webbrowser.open("https://chatgpt.com")

        elif "youtube" in command:
            # Common patterns: "open youtube", "search puppies on youtube"
            match = re.search(r'(?:search|open)\s+(.*?)\s+(?:on|in|directly on)\s+(?:youtube)', command)
            if match:
                query = match.group(1).strip()
                response_msg = f"Searching YouTube for: {query}"
                webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            else:
                response_msg = "Opening YouTube."
                webbrowser.open("https://www.youtube.com")

        elif "chrome" in command or "browser" in command:
            response_msg = "Opening Google Chrome."
            # Prefer webbrowser to start chrome if possible, else os system
            webbrowser.open("http://www.google.com")

        elif any(x in command for x in ["documents", "downloads", "desktop", "folder"]):
            if "documents" in command:
                path = os.path.expanduser("~/Documents")
                os.startfile(path)
                response_msg = "Opening Documents."
            elif "downloads" in command:
                path = os.path.expanduser("~/Downloads")
                os.startfile(path)
                response_msg = "Opening Downloads."
            elif "desktop" in command:
                path = os.path.expanduser("~/Desktop")
                os.startfile(path)
                response_msg = "Opening Desktop."
            else:
                # Absolute path matching if 'folder' is still used
                match_abs = re.search(r'open\s+(.:\\[^\s]+)', command, re.IGNORECASE)
                if match_abs:
                    path = match_abs.group(1)
                    if os.path.exists(path):
                        os.startfile(path)
                        response_msg = f"Opening path: {path}"
                    else:
                        response_msg = f"Path not found: {path}"
                else:
                    response_msg = "I can open Documents, Downloads, Desktop or specific paths like C:\\FolderName"

    except Exception as e:
        import traceback
        print(f"Backend Error in process_command: {str(e)}")
        traceback.print_exc()
        response_msg = f"Internal system error during command execution."
        
    return jsonify({'status': 'success', 'message': response_msg})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
