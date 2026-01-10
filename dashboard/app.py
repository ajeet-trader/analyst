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

# Database
from database import db

# Dashboard config
from dashboard.config import SERVER, DATA, FEATURES

# Journal
from journal import journal

# Risk Management
from risk import risk_manager

# Strategies
from strategies import strategy_engine, BUILTIN_STRATEGIES

# Database Management
from database.db_manager import db_manager

# Sessions
from sessions import session_manager

# App state
app = Flask(__name__)
app.config['SECRET_KEY'] = SERVER['secret_key']
socketio = SocketIO(app, cors_allowed_origins="*")

# Register analytics blueprint
from dashboard.analytics import analytics_bp
app.register_blueprint(analytics_bp)

# Global state (loaded from database on startup)
state = {
    'status': 'Ready',
    'captures': [],
    'current_signal': None,
    'signal_history': [],
    'stats': {'wins': 0, 'losses': 0},
    'providers': [],
    'current_signal_id': None  # Track current signal ID for result updates
}

# Load history from database on startup
def load_history():
    """Load recent signals from database and identify active one"""
    recent = db.get_recent_signals(DATA['history_limit'])
    state['signal_history'] = recent
    
    # Find most recent signal without a result
    active_signals = [s for s in recent if not s.get('result')]
    if active_signals:
        state['current_signal'] = active_signals[0]
        state['current_signal_id'] = active_signals[0].get('id')
    else:
        state['current_signal'] = None
        state['current_signal_id'] = None
        
    stats = db.get_stats()
    state['stats'] = {
        'wins': stats.total_wins,
        'losses': stats.total_losses
    }

load_history()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/analytics')
def analytics():
    """Analytics page"""
    return render_template('analytics.html')


@app.route('/journal')
def journal_page():
    """Journal page"""
    return render_template('journal.html')


@app.route('/risk')
def risk_page():
    """Risk management page"""
    return render_template('risk.html')


@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')


@app.route('/help')
def help_page():
    """Help & Guide page"""
    return render_template('help.html')


@app.route('/sessions')
def sessions_page():
    """Sessions history page"""
    return render_template('sessions.html')


@app.route('/api/journal/recent')
def get_recent_journal():
    """Get recent journal entries"""
    limit = int(request.args.get('limit', 20))
    trades = journal.get_recent_trades(limit)
    return jsonify(trades)


@app.route('/api/risk/settings')
def get_risk_settings():
    """Get user risk settings"""
    return jsonify(risk_manager.settings)


@app.route('/api/risk/settings', methods=['POST'])
def update_risk_settings():
    """Update risk settings"""
    data = request.json
    risk_manager.update_settings(data)
    return jsonify({'success': True, 'settings': risk_manager.settings})


@app.route('/api/risk/daily-status')
def get_daily_status():
    """Get today's trading status"""
    return jsonify(risk_manager.check_daily_status())


@app.route('/api/risk/suggestions')
def get_risk_suggestions():
    """Get personalized suggestions"""
    return jsonify(risk_manager.get_suggestions())


@app.route('/api/risk/position-size')
def get_position_size():
    """Calculate position size for given confidence"""
    confidence = int(request.args.get('confidence', 80))
    return jsonify(risk_manager.calculate_position_size(confidence))


@app.route('/api/strategy/active')
def get_active_strategy():
    """Get active strategy"""
    return jsonify({
        'active_strategy': strategy_engine.active_strategy,
        'strategy': strategy_engine.get_active_strategy()
    })


@app.route('/api/strategy/active', methods=['POST'])
def set_active_strategy():
    """Set active strategy"""
    data = request.json
    strategy_name = data.get('strategy')
    success = strategy_engine.set_active_strategy(strategy_name)
    return jsonify({'success': success, 'active_strategy': strategy_engine.active_strategy})


@app.route('/api/strategy/all')
def get_all_strategies():
    """Get all available strategies"""
    return jsonify(strategy_engine.get_all_strategies())


@app.route('/api/database/stats')
def get_database_stats():
    """Get database statistics"""
    return jsonify(db_manager.get_database_stats())


@app.route('/api/database/reset', methods=['POST'])
def reset_database():
    """Reset entire database"""
    data = request.json
    confirm = data.get('confirm', False)
    res = db_manager.reset_database(confirm)
    if res.get('success'):
        load_history()
        socketio.emit('state_update', state)
        socketio.emit('stats_update', state['stats'])
        socketio.emit('history_update', {'history': state['signal_history']})
    return jsonify(res)


@app.route('/api/database/cleanup', methods=['POST'])
def cleanup_database():
    """Cleanup old data"""
    days = int(request.args.get('days', 90))
    return jsonify(db_manager.cleanup_old_data(days))


@app.route('/api/database/delete-signal/<int:signal_id>', methods=['DELETE'])
def delete_signal_api(signal_id):
    """Delete a specific signal"""
    return jsonify(db_manager.delete_signal(signal_id))


@app.route('/api/sessions/active')
def get_active_session():
    """Get active session"""
    session = session_manager.get_active_session()
    return jsonify(session if session else {})


@app.route('/api/sessions/start', methods=['POST'])
def start_session():
    """Start new session"""
    data = request.json
    session_name = data.get('session_name', f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    from strategies import strategy_engine
    from risk import risk_manager
    
    session_id = session_manager.start_session(
        session_name=session_name,
        strategy_name=strategy_engine.active_strategy,
        risk_settings=risk_manager.settings
    )
    
    return jsonify({'success': True, 'session_id': session_id})


@app.route('/api/sessions/<int:session_id>/pause', methods=['POST'])
def pause_session(session_id):
    """Pause session"""
    success = session_manager.pause_session(session_id)
    return jsonify({'success': success})


@app.route('/api/sessions/<int:session_id>/resume', methods=['POST'])
def resume_session(session_id):
    """Resume session"""
    success = session_manager.resume_session(session_id)
    return jsonify({'success': success})


@app.route('/api/sessions/<int:session_id>/end', methods=['POST'])
def end_session(session_id):
    """End session"""
    data = request.json
    notes = data.get('notes', '')
    success = session_manager.end_session(session_id, notes)
    return jsonify({'success': success})


@app.route('/api/sessions/all')
def get_all_sessions():
    """Get all sessions"""
    limit = int(request.args.get('limit', 50))
    sessions = session_manager.get_all_sessions(limit)
    return jsonify(sessions)


@app.route('/api/sessions/<int:session_id>/details')
def get_session_details(session_id):
    """Get session details"""
    details = session_manager.get_session_details(session_id)
    return jsonify(details if details else {})


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


@app.route('/archive/<path:filepath>')
def serve_archive(filepath):
    """Serve archived journal images"""
    from journal.journal_manager import ARCHIVES_DIR
    file_path = ARCHIVES_DIR / filepath
    if file_path.exists() and file_path.suffix in ['.png', '.jpg', '.jpeg']:
        return send_file(file_path, mimetype=f'image/{file_path.suffix[1:]}')
    return "Not found", 404


@app.route('/api/history')
def get_history():
    """Get recent signal history and statistics"""
    limit = int(request.args.get('limit', DATA['history_limit']))
    signals = db.get_recent_signals(limit)
    stats = db.get_stats()
    
    return jsonify({
        'signals': signals,
        'stats': {
            'total_signals': stats.total_signals,
            'wins': stats.total_wins,
            'losses': stats.total_losses,
            'win_rate': stats.win_rate
        }
    })


@app.route('/api/signals/<int:signal_id>/result', methods=['POST'])
def set_signal_result(signal_id):
    """Update the result of a signal"""
    data = request.json
    result = data.get('result')
    user_note = data.get('user_note', data.get('note', ''))
    
    if result not in ['win', 'loss', 'draw']:
        return jsonify({'success': False, 'error': 'Invalid result'}), 400
        
    success = db.update_signal_result(signal_id, result, user_note)
    
    if success:
        # Update journal
        try:
            journal.update_result(signal_id, result, user_note)
        except Exception as e:
            print(f"Journal update failed: {e}")
            
        # Update global state stats for broadcast
        if result == 'win':
            state['stats']['wins'] += 1
        elif result == 'loss':
            state['stats']['losses'] += 1
        
        if state.get('current_signal_id') == signal_id:
            state['current_signal'] = None
            state['current_signal_id'] = None
            
        # Reload history to keep state in sync
        load_history()
        
        # Broadcast update
        socketio.emit('state_update', state) # Send full state update to clear UI
        socketio.emit('stats_update', state['stats'])
        socketio.emit('history_update', {'history': state['signal_history']})
        
        return jsonify({'success': True, 'stats': state['stats']})
    
    return jsonify({'success': False, 'error': 'Signal not found'}), 404


@app.route('/api/signal/result', methods=['POST'])
def record_result():
    """Legacy endpoint wrapper for the dashboard"""
    if state.get('current_signal_id'):
        return set_signal_result(state['current_signal_id'])
    return jsonify({'success': False, 'error': 'No active signal on dashboard'}), 400


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


def emit_signal(signal_data: dict, chart_paths: list = None):
    """Broadcast new signal and save to database (with strategy filtering)"""
    
    # Filter through active strategy
    passes, reason = strategy_engine.filter_signal(signal_data)
    if not passes:
        # Signal rejected by strategy
        print(f"\n⚠️ Signal rejected by strategy: {reason}")
        emit_status(f"Signal filtered: {reason}")
        return  # Don't emit or save
    
    # Save to database
    signal_id = db.save_signal(signal_data, chart_paths)
    state['current_signal_id'] = signal_id
    
    # Start journal entry (archive charts)
    if chart_paths:
        journal.start_trade(signal_id, signal_data, chart_paths)
    
    # Add to state
    signal_data['id'] = signal_id
    signal_data['timestamp'] = datetime.now().isoformat()
    state['current_signal'] = signal_data
    state['signal_history'].insert(0, signal_data)
    if len(state['signal_history']) > DATA['history_limit']:
        state['signal_history'] = state['signal_history'][:DATA['history_limit']]
    
    socketio.emit('signal_update', {
        'signal': signal_data,
        'timestamp': signal_data['timestamp']
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


def run_dashboard(host=None, port=None, open_browser=None):
    """Start the dashboard server"""
    # Use config defaults if not provided
    host = host or SERVER['host']
    port = port or SERVER['port']
    open_browser = open_browser if open_browser is not None else SERVER['auto_open_browser']
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
