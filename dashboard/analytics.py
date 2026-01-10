"""
Analytics and Statistics API
=============================
Advanced statistics and chart data
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from collections import defaultdict
import json

from database import db
from dashboard.config import DATA

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/api/analytics/overview')
def get_overview():
    """Get overview statistics"""
    stats = db.get_stats()
    
    return jsonify({
        'total_signals': stats.total_signals,
        'total_wins': stats.total_wins,
        'total_losses': stats.total_losses,
        'win_rate': round(stats.win_rate, 1),
        'total_trades': stats.total_wins + stats.total_losses
    })


@analytics_bp.route('/api/analytics/by-asset')
def get_by_asset():
    """Get statistics grouped by asset"""
    cursor = db.conn.cursor()
    
    cursor.execute("""
        SELECT 
            asset,
            COUNT(*) as total,
            SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses
        FROM signals
        WHERE result IS NOT NULL
        GROUP BY asset
        ORDER BY total DESC
        LIMIT ?
    """, (DATA['analytics_asset_limit'],))
    
    rows = cursor.fetchall()
    
    data = []
    for row in rows:
        total = row['wins'] + row['losses']
        win_rate = (row['wins'] / total * 100) if total > 0 else 0
        data.append({
            'asset': row['asset'],
            'total': total,
            'wins': row['wins'],
            'losses': row['losses'],
            'win_rate': round(win_rate, 1)
        })
    
    return jsonify(data)


@analytics_bp.route('/api/analytics/by-pattern')
def get_by_pattern():
    """Get statistics by pattern"""
    cursor = db.conn.cursor()
    
    cursor.execute("""
        SELECT patterns_detected, result
        FROM signals
        WHERE patterns_detected IS NOT NULL
        AND patterns_detected != '[]'
        AND result IN ('win', 'loss')
    """)
    
    rows = cursor.fetchall()
    
    # Count by pattern
    pattern_stats = defaultdict(lambda: {'wins': 0, 'losses': 0})
    
    for row in rows:
        try:
            patterns = json.loads(row['patterns_detected'])
            for pattern in patterns:
                if row['result'] == 'win':
                    pattern_stats[pattern]['wins'] += 1
                else:
                    pattern_stats[pattern]['losses'] += 1
        except:
            pass
    
    # Format response
    data = []
    for pattern, stats in pattern_stats.items():
        total = stats['wins'] + stats['losses']
        win_rate = (stats['wins'] / total * 100) if total > 0 else 0
        data.append({
            'pattern': pattern.replace('_', ' ').title(),
            'total': total,
            'wins': stats['wins'],
            'losses': stats['losses'],
            'win_rate': round(win_rate, 1)
        })
    
    # Sort by total
    data.sort(key=lambda x: x['total'], reverse=True)
    
    return jsonify(data[:DATA['analytics_pattern_limit']])


@analytics_bp.route('/api/analytics/timeline')
def get_timeline():
    """Get win/loss timeline for last 30 days"""
    cursor = db.conn.cursor()
    
    # Get timeline days from config
    cursor.execute("""
        SELECT 
            DATE(timestamp) as date,
            SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses
        FROM signals
        WHERE timestamp >= DATE('now', ? || ' days')
        AND result IS NOT NULL
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
    """, (f"-{DATA['timeline_days']}",))
    
    rows = cursor.fetchall()
    
    data = []
    for row in rows:
        total = row['wins'] + row['losses']
        win_rate = (row['wins'] / total * 100) if total > 0 else 0
        data.append({
            'date': row['date'],
            'wins': row['wins'],
            'losses': row['losses'],
            'win_rate': round(win_rate, 1)
        })
    
    return jsonify(data)


@analytics_bp.route('/api/signals/filter')
def filter_signals():
    """Filter signals with query parameters"""
    asset = request.args.get('asset')
    result = request.args.get('result')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = int(request.args.get('limit', 50))
    
    query = "SELECT * FROM signals WHERE 1=1"
    params = []
    
    if asset:
        query += " AND asset = ?"
        params.append(asset)
    
    if result:
        query += " AND result = ?"
        params.append(result)
    
    if start_date:
        query += " AND DATE(timestamp) >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND DATE(timestamp) <= ?"
        params.append(end_date)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor = db.conn.cursor()
    cursor.execute(query, params)
    
    rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows])
