# Entry point for the BoxChat application

from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    print("[SERVER STARTUP] Starting BoxChat...")
    print("[SERVER CONFIG] Socket.IO running on port 5000")
    socketio.run(app, allow_unsafe_werkzeug=True, debug=False)

