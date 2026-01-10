"""
Trading Journal Manager
=======================
Automatic capture and archiving of trade data
"""
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import json

from config import CACHE_DIR

# Journal configuration
JOURNAL_DIR = Path(CACHE_DIR).parent / "journal"
ARCHIVES_DIR = JOURNAL_DIR / "archives"

# Ensure directories exist
JOURNAL_DIR.mkdir(exist_ok=True)
ARCHIVES_DIR.mkdir(exist_ok=True)


class JournalManager:
    """Manages automatic trade journaling"""
    
    def __init__(self):
        self.current_trade = None
    
    def start_trade(self, signal_id: int, signal_data: dict, chart_paths: List[str]):
        """
        Start a new trade journal entry
        
        Args:
            signal_id: Database signal ID
            signal_data: Signal details
            chart_paths: List of chart image paths
        """
        timestamp = datetime.now()
        trade_dir = ARCHIVES_DIR / f"trade_{signal_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        trade_dir.mkdir(exist_ok=True)
        
        # Copy charts to archive
        archived_charts = []
        for i, chart_path in enumerate(chart_paths):
            if Path(chart_path).exists():
                dest = trade_dir / f"chart_{i+1}.png"
                shutil.copy2(chart_path, dest)
                archived_charts.append(str(dest))
        
        # Create trade metadata
        trade_meta = {
            'signal_id': signal_id,
            'timestamp': timestamp.isoformat(),
            'direction': signal_data.get('direction'),
            'asset': signal_data.get('asset'),
            'confidence': signal_data.get('confidence'),
            'expiry': signal_data.get('expiry'),
            'entry_timing': signal_data.get('entry_timing'),
            'reasoning': signal_data.get('reasoning'),
            'patterns_detected': signal_data.get('patterns_detected', []),
            'key_levels': signal_data.get('key_levels', []),
            'provider': signal_data.get('provider'),
            'analysis_time_ms': signal_data.get('analysis_time_ms'),
            'charts': archived_charts,
            'result': None,
            'user_note': None,
            'post_analysis': None
        }
        
        # Save metadata
        meta_file = trade_dir / "trade_meta.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(trade_meta, f, indent=2)
        
        self.current_trade = {
            'id': signal_id,
            'dir': trade_dir,
            'meta': trade_meta
        }
        
        return trade_dir
    
    def update_result(self, signal_id: int, result: str, user_note: str = None):
        """
        Update trade result (win/loss)
        
        Args:
            signal_id: Signal ID
            result: 'win' or 'loss'
            user_note: Optional user note
        """
        # Find trade directory
        trade_dirs = list(ARCHIVES_DIR.glob(f"trade_{signal_id}_*"))
        if not trade_dirs:
            return
        
        trade_dir = trade_dirs[0]
        meta_file = trade_dir / "trade_meta.json"
        
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            meta['result'] = result
            meta['user_note'] = user_note
            meta['completed_at'] = datetime.now().isoformat()
            
            # Save updated metadata
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)
            
            # Generate post-trade analysis (lightweight, no AI for now)
            self._generate_post_analysis(trade_dir, meta)
    
    def _generate_post_analysis(self, trade_dir: Path, meta: dict):
        """Generate simple post-trade analysis"""
        result = meta.get('result', 'unknown')
        confidence = meta.get('confidence', 0)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'trade_outcome': result,
            'confidence_vs_result': {
                'confidence': confidence,
                'result': result,
                'match': (result == 'win' and confidence >= 75) or (result == 'loss' and confidence < 75)
            },
            'suggestions': []
        }
        
        # Simple rule-based suggestions
        if result == 'loss':
            if confidence >= 80:
                analysis['suggestions'].append("High confidence loss - review pattern recognition")
            if len(meta.get('patterns_detected', [])) == 0:
                analysis['suggestions'].append("No patterns detected - consider waiting for clearer setups")
        elif result == 'win':
            if confidence < 70:
                analysis['suggestions'].append("Low confidence win - good entry despite uncertainty")
        
        # Save analysis
        analysis_file = trade_dir / "post_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        # Also update meta
        meta['post_analysis'] = analysis
        meta_file = trade_dir / "trade_meta.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)
    
    def get_trade_summary(self, signal_id: int) -> Optional[dict]:
        """Get complete trade summary"""
        trade_dirs = list(ARCHIVES_DIR.glob(f"trade_{signal_id}_*"))
        if not trade_dirs:
            return None
        
        meta_file = trade_dirs[0] / "trade_meta.json"
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def get_recent_trades(self, limit: int = 10) -> List[dict]:
        """Get recent trade summaries"""
        trade_dirs = sorted(ARCHIVES_DIR.glob("trade_*"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        trades = []
        for trade_dir in trade_dirs[:limit]:
            meta_file = trade_dir / "trade_meta.json"
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    meta['trade_dir'] = str(trade_dir)
                    trades.append(meta)
        
        return trades


# Global journal instance
journal = JournalManager()
