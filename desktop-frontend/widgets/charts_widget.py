"""
Charts Widget for displaying Matplotlib visualizations.
Premium design matching web frontend chart cards.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QMenu, QFileDialog, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

from config import COLORS, CHART_COLORS, RADIUS, SPACING


class ChartCard(QFrame):
    """Premium styled chart card matching web frontend."""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title_text = title
        self.setMinimumHeight(380)
        self.setup_ui()
        self._apply_style()
    
    def _apply_style(self):
        self.setStyleSheet(f"""
            ChartCard {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_highlight']};
                border-radius: {RADIUS['lg']}px;
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        layout.setSpacing(SPACING['md'])
        
        # Header with title and export button
        header = QHBoxLayout()
        
        title = QLabel(self.title_text)
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        header.addWidget(title)
        
        header.addStretch()
        
        # Export button
        self.export_btn = QPushButton("📥")
        self.export_btn.setFixedSize(36, 36)
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
        """)
        self.export_btn.clicked.connect(self.show_export_menu)
        header.addWidget(self.export_btn)
        
        layout.addLayout(header)
        
        # Top accent line
        accent = QFrame()
        accent.setFixedHeight(2)
        accent.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
            border-radius: 1px;
        """)
        layout.addWidget(accent)
        
        # Chart canvas container
        self.canvas_container = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_container)
        self.canvas_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.canvas_container, 1)
    
    def set_canvas(self, canvas):
        """Set the matplotlib canvas for this card."""
        # Clear existing
        while self.canvas_layout.count():
            item = self.canvas_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.canvas_layout.addWidget(canvas)
        self.canvas = canvas
    
    def show_export_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {COLORS['bg_glass_strong']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                padding: 8px;
            }}
            QMenu::item {{
                padding: 10px 20px;
                border-radius: {RADIUS['sm']}px;
                color: {COLORS['text_secondary']};
            }}
            QMenu::item:selected {{
                background: rgba(99, 102, 241, 0.1);
                color: {COLORS['primary']};
            }}
        """)
        
        png_action = menu.addAction("📷 Export as PNG")
        svg_action = menu.addAction("📐 Export as SVG")
        pdf_action = menu.addAction("📄 Export as PDF")
        
        action = menu.exec_(self.export_btn.mapToGlobal(self.export_btn.rect().bottomLeft()))
        
        if hasattr(self, 'canvas') and action:
            if action == png_action:
                self.export_chart('png')
            elif action == svg_action:
                self.export_chart('svg')
            elif action == pdf_action:
                self.export_chart('pdf')
    
    def export_chart(self, format):
        file_filter = {
            'png': 'PNG Files (*.png)',
            'svg': 'SVG Files (*.svg)',
            'pdf': 'PDF Files (*.pdf)'
        }
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Chart as {format.upper()}",
            f"chart.{format}",
            file_filter[format]
        )
        
        if filepath:
            self.canvas.fig.savefig(filepath, format=format, dpi=150, 
                                    facecolor=COLORS['bg_dark'], edgecolor='none',
                                    bbox_inches='tight')


class PremiumChartCanvas(FigureCanvas):
    """Matplotlib canvas with premium dark theme styling."""
    
    def __init__(self, parent=None, width=8, height=5):
        self.fig = Figure(figsize=(width, height), facecolor=COLORS['bg_card'])
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.style_axes()
    
    def style_axes(self):
        """Apply premium dark theme styling to axes."""
        self.ax.set_facecolor(COLORS['bg_card'])
        self.ax.tick_params(colors=COLORS['text_secondary'], labelsize=9)
        
        for spine in self.ax.spines.values():
            spine.set_color(COLORS['border'])
            spine.set_linewidth(0.5)
        
        self.ax.xaxis.label.set_color(COLORS['text_primary'])
        self.ax.yaxis.label.set_color(COLORS['text_primary'])
        self.ax.title.set_color(COLORS['text_primary'])
        
        # Grid styling
        self.ax.grid(True, alpha=0.1, color='white', linestyle='-', linewidth=0.5)
        self.ax.set_axisbelow(True)


class ChartsWidget(QWidget):
    """Widget containing all chart visualizations with premium styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['lg'])
        
        # Type distribution chart card
        self.type_card = ChartCard("Equipment Type Distribution")
        self.type_canvas = PremiumChartCanvas()
        self.type_card.set_canvas(self.type_canvas)
        layout.addWidget(self.type_card)
        
        # Averages chart card
        self.avg_card = ChartCard("Average Parameter Values")
        self.avg_canvas = PremiumChartCanvas()
        self.avg_card.set_canvas(self.avg_canvas)
        layout.addWidget(self.avg_card)
    
    def update_charts(self, summary: dict):
        """Update all charts with summary data."""
        self.update_type_chart(summary.get('type_distribution', {}))
        self.update_averages_chart(summary.get('averages', {}))
    
    def update_type_chart(self, type_distribution: dict):
        """Update the type distribution chart with premium styling."""
        self.type_canvas.ax.clear()
        self.type_canvas.style_axes()
        
        if not type_distribution:
            self.type_canvas.ax.text(
                0.5, 0.5, 'No data available',
                ha='center', va='center',
                color=COLORS['text_muted'],
                fontsize=14, transform=self.type_canvas.ax.transAxes
            )
            self.type_canvas.draw()
            return
        
        types = [t.replace('_', ' ').title() for t in type_distribution.keys()]
        counts = list(type_distribution.values())
        colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(types))]
        
        # Create bars with gradient effect
        bars = self.type_canvas.ax.bar(
            types, counts, color=colors,
            edgecolor='white', linewidth=0.5,
            alpha=0.9
        )
        
        # Add value labels
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            self.type_canvas.ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + max(counts) * 0.02,
                str(int(count)),
                ha='center', va='bottom',
                color=COLORS['text_primary'],
                fontweight='bold',
                fontsize=10
            )
        
        self.type_canvas.ax.set_xlabel('Equipment Type', fontsize=11, fontweight='bold', 
                                        color=COLORS['text_secondary'])
        self.type_canvas.ax.set_ylabel('Count', fontsize=11, fontweight='bold',
                                        color=COLORS['text_secondary'])
        self.type_canvas.ax.set_ylim(0, max(counts) * 1.2)
        
        plt.setp(self.type_canvas.ax.xaxis.get_majorticklabels(), rotation=30, ha='right')
        
        self.type_canvas.fig.tight_layout(pad=2)
        self.type_canvas.draw()
    
    def update_averages_chart(self, averages: dict):
        """Update the averages chart with premium styling."""
        self.avg_canvas.ax.clear()
        self.avg_canvas.style_axes()
        
        if not averages:
            self.avg_canvas.ax.text(
                0.5, 0.5, 'No data available',
                ha='center', va='center',
                color=COLORS['text_muted'],
                fontsize=14, transform=self.avg_canvas.ax.transAxes
            )
            self.avg_canvas.draw()
            return
        
        params = [p.replace('_', ' ').title() for p in averages.keys()]
        values = list(averages.values())
        
        # Use gradient-like colors
        colors = ['#3b82f6', '#10b981', '#f43f5e', '#f59e0b', '#8b5cf6'][:len(params)]
        
        bars = self.avg_canvas.ax.bar(
            params, values, color=colors,
            edgecolor='white', linewidth=0.5,
            alpha=0.9
        )
        
        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            self.avg_canvas.ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + max(values) * 0.02,
                f'{val:.2f}',
                ha='center', va='bottom',
                color=COLORS['text_primary'],
                fontweight='bold',
                fontsize=10
            )
        
        self.avg_canvas.ax.set_xlabel('Parameter', fontsize=11, fontweight='bold',
                                       color=COLORS['text_secondary'])
        self.avg_canvas.ax.set_ylabel('Average Value', fontsize=11, fontweight='bold',
                                       color=COLORS['text_secondary'])
        self.avg_canvas.ax.set_ylim(0, max(values) * 1.2)
        
        # Rotate labels to prevent overlap
        plt.setp(self.avg_canvas.ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        self.avg_canvas.fig.tight_layout(pad=2)
        self.avg_canvas.draw()
    
    def clear_charts(self):
        """Clear all charts."""
        for canvas in [self.type_canvas, self.avg_canvas]:
            canvas.ax.clear()
            canvas.style_axes()
            canvas.ax.text(
                0.5, 0.5, 'Select a dataset to view charts',
                ha='center', va='center',
                color=COLORS['text_muted'],
                fontsize=12, transform=canvas.ax.transAxes
            )
            canvas.draw()
