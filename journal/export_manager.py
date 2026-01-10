"""
Journal Export Manager
=====================
Export journal entries and trading signals to various formats
"""
import io
import csv
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ExportManager:
    """Handle export operations for journal and signals"""
    
    def __init__(self):
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
    
    def export_to_csv(self, signals: List[Dict]) -> io.BytesIO:
        """
        Export signals to CSV format
        Returns BytesIO object
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Timestamp', 'Asset', 'Direction', 'Confidence', 'Expiry', 
            'Result', 'Entry Timing', 'Note'
        ])
        
        # Write data
        for signal in signals:
            writer.writerow([
                signal.get('timestamp', ''),
                signal.get('asset', ''),
                signal.get('direction', ''),
                f"{signal.get('confidence', 0)}%",
                signal.get('expiry', ''),
                signal.get('result', 'pending'),
                signal.get('entry_timing', ''),
                signal.get('user_note', '')
            ])
        
        # Convert to BytesIO
        output.seek(0)
        bytes_output = io.BytesIO(output.getvalue().encode('utf-8'))
        return bytes_output
    
    def export_to_pdf(self, signals: List[Dict], notes: List[Dict] = None, 
                     stats: Dict = None) -> Optional[io.BytesIO]:
        """
        Export complete journal to PDF
        Returns BytesIO object or None if reportlab not available
        """
        if not REPORTLAB_AVAILABLE:
            return None
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Trading Journal Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", 
                              self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Statistics Section
        if stats:
            story.append(Paragraph("Performance Summary", self.styles['Heading2']))
            stats_data = [
                ['Total Signals', str(stats.get('total_signals', 0))],
                ['Wins', str(stats.get('total_wins', 0))],
                ['Losses', str(stats.get('total_losses', 0))],
                ['Win Rate', f"{stats.get('win_rate', 0):.1f}%"]
            ]
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.white)
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Signals Section
        if signals:
            story.append(Paragraph("Trading Signals", self.styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for signal in signals:
                # Signal header
                direction = signal.get('direction', 'N/A')
                asset = signal.get('asset', 'N/A')
                confidence = signal.get('confidence', 0)
                result = signal.get('result', 'pending')
                
                color = colors.HexColor('#10b981') if result == 'win' else \
                        colors.HexColor('#ef4444') if result == 'loss' else colors.gray
                
                signal_header = Paragraph(
                    f"<b>{direction}</b> {asset} • {confidence}% Confidence",
                    self.styles['Heading3']
                )
                story.append(signal_header)
                
                # Signal details
                details = [
                    ['Timestamp', signal.get('timestamp', 'N/A')],
                    ['Expiry', signal.get('expiry', 'N/A')],
                    ['Entry Timing', signal.get('entry_timing', 'N/A')],
                    ['Result', result.upper()],
                ]
                
                details_table = Table(details, colWidths=[1.5*inch, 4*inch])
                details_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('TEXTCOLOR', (1, 3), (1, 3), color),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(details_table)
                
                # Reasoning
                if signal.get('reasoning'):
                    story.append(Paragraph("<b>Analysis:</b>", self.styles['Normal']))
                    story.append(Paragraph(signal['reasoning'], self.styles['Normal']))
                
                # User note
                if signal.get('user_note'):
                    story.append(Spacer(1, 0.1*inch))
                    note_style = ParagraphStyle(
                        'Note',
                        parent=self.styles['Normal'],
                        fontSize=10,
                        textColor=colors.HexColor('#64748b'),
                        leftIndent=20
                    )
                    story.append(Paragraph(f"<i>Note: {signal['user_note']}</i>", note_style))
                
                story.append(Spacer(1, 0.2*inch))
        
        # Journal Notes Section
        if notes:
            story.append(PageBreak())
            story.append(Paragraph("Journal Entries", self.styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for note in notes:
                title = note.get('title', 'Untitled Entry')
                content = note.get('content', '')
                timestamp = note.get('timestamp', '')
                
                story.append(Paragraph(f"<b>{title}</b>", self.styles['Heading3']))
                story.append(Paragraph(f"<i>{timestamp}</i>", self.styles['Normal']))
                story.append(Spacer(1, 0.05*inch))
                story.append(Paragraph(content, self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_trade_card(self, signal: Dict, output_path: Optional[Path] = None) -> Optional[io.BytesIO]:
        """
        Generate a shareable trade card image
        Returns BytesIO object or None if PIL not available
        """
        if not PIL_AVAILABLE:
            return None
        
        # Card dimensions
        width, height = 600, 400
        img = Image.new('RGB', (width, height), color='#0f172a')
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a better font
            title_font = ImageFont.truetype("arial.ttf", 48)
            subtitle_font = ImageFont.truetype("arial.ttf", 24)
            text_font = ImageFont.truetype("arial.ttf", 18)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Direction and color
        direction = signal.get('direction', 'N/A')
        result = signal.get('result', 'pending')
        
        if direction == 'CALL':
            accent_color = '#10b981'
            arrow = '▲'
        elif direction == 'PUT':
            accent_color = '#ef4444'
            arrow = '▼'
        else:
            accent_color = '#64748b'
            arrow = '●'
        
        # Draw direction banner
        draw.rectangle([(0, 0), (width, 100)], fill=accent_color)
        draw.text((300, 50), f"{arrow} {direction}", fill='white', font=title_font, anchor='mm')
        
        # Asset and confidence
        asset = signal.get('asset', 'Unknown')
        confidence = signal.get('confidence', 0)
        draw.text((300, 150), asset, fill='white', font=subtitle_font, anchor='mm')
        draw.text((300, 190), f"{confidence}% Confidence", fill='#94a3b8', font=text_font, anchor='mm')
        
        # Expiry and result
        expiry = signal.get('expiry', 'N/A')
        draw.text((150, 250), f"Expiry: {expiry}", fill='#cbd5e1', font=text_font, anchor='mm')
        
        result_color = '#10b981' if result == 'win' else '#ef4444' if result == 'loss' else '#94a3b8'
        draw.text((450, 250), f"Result: {result.upper()}", fill=result_color, font=text_font, anchor='mm')
        
        # User note (if present)
        if signal.get('user_note'):
            note = signal['user_note'][:60] + '...' if len(signal['user_note']) > 60 else signal['user_note']
            draw.text((300, 310), f'"{note}"', fill='#64748b', font=text_font, anchor='mm')
        
        # Branding
        draw.text((300, 370), "AI Trading Analyst", fill='#475569', font=text_font, anchor='mm')
        
        # Save or return
        if output_path:
            img.save(output_path, 'PNG')
            return None
        else:
            buffer = io.BytesIO()
            img.save(buffer, 'PNG')
            buffer.seek(0)
            return buffer


# Global export manager instance
export_manager = ExportManager()
