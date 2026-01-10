"""
Dashboard Configuration
=======================
All UI settings, colors, and behavior configs
"""

# === UI Theme Configuration ===
THEME = {
    'colors': {
        'bg_primary': '#0a0e27',
        'bg_secondary': '#151a35',
        'bg_card': '#1a1f3a',
        'border': '#2d3a5f',
        'text_primary': '#ffffff',
        'text_secondary': '#9ca3b8',
        'accent_green': '#10b981',
        'accent_red': '#ef4444',
        'accent_blue': '#3b82f6',
        'accent_yellow': '#f59e0b',
        'accent_purple': '#8b5cf6'
    },
    'fonts': {
        'primary': 'Segoe UI, -apple-system, BlinkMacSystemFont, sans-serif',
        'monospace': 'Courier New, monospace'
    }
}

# === Dashboard Layout ===
LAYOUT = {
    'max_width': '1400px',
    'card_gap': '20px',
    'card_padding': '20px',
    'border_radius': '15px'
}

# === Data Display Settings ===
DATA = {
    'history_limit': 20,
    'analytics_asset_limit': 10,
    'analytics_pattern_limit': 10,
    'timeline_days': 30,
    'chart_refresh_interval': 5000  # ms
}

# === Notification Settings ===
NOTIFICATIONS = {
    'desktop_enabled': True,
    'auto_dismiss_seconds': 20,
    'sound_enabled': True,
    'toast_duration': 'long'  # short, long
}

# === Analytics Configuration ===
ANALYTICS = {
    'charts': {
        'asset_performance': True,
        'pattern_performance': True,
        'timeline': True,
        'win_rate_by_expiry': False  # Future feature
    },
    'export_formats': ['csv', 'json'],  # Future: 'pdf'
    'date_range_presets': [
        {'label': 'Today', 'days': 0},
        {'label': 'Last 7 Days', 'days': 7},
        {'label': 'Last 30 Days', 'days': 30},
        {'label': 'Last 90 Days', 'days': 90}
    ]
}

# === Server Configuration ===
SERVER = {
    'host': '127.0.0.1',
    'port': 5000,
    'debug': False,
    'auto_open_browser': True,
    'secret_key': 'analyst-ai-secret-key-2024'
}

# === Database Configuration ===
DATABASE = {
    'type': 'sqlite',  # Future: 'postgresql'
    'filename': 'signals.db',
    'backup_enabled': False,
    'backup_interval_hours': 24
}

# === Hotkey Configuration ===
HOTKEYS = {
    'capture': 'aa',
    'analyze': 'c',
    'clear': 'x',
    'view_cache': 'v',
    'quit': 'q'
}

# === Feature Flags ===
FEATURES = {
    'analytics_page': True,
    'journal_page': False,  # Phase 3
    'export_signals': True,
    'webhooks': False,  # n8n integration
    'multi_user': False  # Future
}

# === Chart Display ===
CHARTS = {
    'asset_chart_type': 'bar',  # bar, line, pie
    'pattern_chart_type': 'horizontalBar',
    'timeline_chart_type': 'line',
    'show_grid': True,
    'animate': True
}
