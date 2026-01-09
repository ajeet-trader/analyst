"""
Flask Web Dashboard for AI Trading Analyst
==========================================
Modern web-based UI with real-time updates via SocketIO
"""
from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import threading
import webbrowser
from pathlib import Path
import json
from datetime import datetime

# App state
app = Flask(__name__)
app.config['SECRET_KEY'] = 'analyst-ai-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
state = {
    'status': 'Ready',
    'captures': [],
    'current_signal': None,
    'signal_history': [],
    'stats': {'wins': 0, 'losses': 0},
    'providers': []
}


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current system status"""
    return jsonify(state)


@app.route('/cache/<filename>')
def serve_image(filename):
    """Serve cached images"""
    from config import CACHE_DIR
    file_path = Path(CACHE_DIR) / filename
    if file_path.exists():
        return send_file(file_path, mimetype='image/png')
    return "Not found", 404


@app.route('/api/signal/result', methods=['POST'])
def record_result():
    """Record win/loss for a signal"""
    data = request.json
    result = data.get('result')  # 'win' or 'loss'
   
    if result == 'win':
        state['stats']['wins'] += 1
    elif result == 'loss':
        state['stats']['losses'] += 1
    
    # Broadcast update
    socketio.emit('stats_update', state['stats'])
    
    return jsonify({'success': True, 'stats': state['stats']})


# ===== WebSocket Events =====

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print(f"Dashboard client connected")
    emit('state_update', state)


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print("Dashboard client disconnected")


def emit_status(status: str):
    """Broadcast status update"""
    state['status'] = status
    socketio.emit('status_update', {'status': status})


def emit_captures(captures: list):
    """Broadcast captures update"""
    state['captures'] = captures
    socketio.emit('captures_update', {'captures': captures, 'count': len(captures)})


def emit_signal(signal_data: dict):
    """Broadcast new signal"""
    state['current_signal'] = signal_data
    state['signal_history'].insert(0, signal_data)
    if len(state['signal_history']) > 20:
        state['signal_history'] = state['signal_history'][:20]
    
    socketio.emit('signal_update', {
        'signal': signal_data,
        'timestamp': datetime.now().isoformat()
    })
    
    # Also broadcast history update
    socketio.emit('history_update', {'history': state['signal_history']})


def emit_error(error: str):
    """Broadcast error"""
    socketio.emit('error_update', {'error': error})


def emit_providers(providers: list):
    """Broadcast available providers"""
    state['providers'] = providers
    socketio.emit('providers_update', {'providers': providers})


def run_dashboard(host='127.0.0.1', port=5000, open_browser=True):
    """Start the dashboard server"""
    def start_server():
        socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
    
    # Start server in thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Open browser
    if open_browser:
        url = f"http://{host}:{port}"
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
        print(f"\n🌐 Dashboard running at: {url}")
        print("Press Ctrl+C in the console to quit\n")
    
    return server_thread


if __name__ == "__main__":
    run_dashboard()
