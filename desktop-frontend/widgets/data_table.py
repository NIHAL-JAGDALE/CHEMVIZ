"""
Data Table Widget for displaying CSV data.
Premium design matching web frontend DataTable.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QLabel, QLineEdit, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from config import COLORS, RADIUS, SPACING


class DataTableWidget(QWidget):
    """Widget for displaying tabular data with premium styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['md'])
        
        # Header with title and search
        header = QHBoxLayout()
        
        title = QLabel("Raw Data")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        header.addWidget(title)
        
        header.addStretch()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search data...")
        self.search_input.setFixedWidth(250)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                padding: 8px 16px;
                color: {COLORS['text_primary']};
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """)
        self.search_input.textChanged.connect(self.filter_table)
        header.addWidget(self.search_input)
        
        layout.addLayout(header)
        
        # Table container with shadow
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['lg']}px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        table_container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(table_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Table widget
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setMouseTracking(True)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_card']};
                border: none;
                border-radius: {RADIUS['lg']}px;
                color: {COLORS['text_primary']};
                font-size: 12px;
                gridline-color: transparent;
            }}
            QTableWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QTableWidget::item:selected {{
                background-color: rgba(99, 102, 241, 0.2);
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:hover {{
                background-color: rgba(99, 102, 241, 0.1);
            }}
            QHeaderView::section {{
                background-color: rgba(15, 23, 42, 0.5);
                color: {COLORS['text_secondary']};
                padding: 14px 16px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: {RADIUS['lg']}px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: {RADIUS['lg']}px;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['bg_card']};
                width: 8px;
                border-radius: 4px;
                margin: 4px 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['text_muted']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {COLORS['bg_card']};
                height: 8px;
                border-radius: 4px;
                margin: 2px 4px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {COLORS['border']};
                border-radius: 4px;
                min-width: 30px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)
        
        container_layout.addWidget(self.table)
        layout.addWidget(table_container)
        
        # Row count label
        self.row_count_label = QLabel("0 records")
        self.row_count_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(self.row_count_label)
    
    def load_data(self, columns: list, data: list):
        """Load data into the table."""
        self.all_data = data
        self.columns = columns
        
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        for row_idx, row_data in enumerate(data):
            for col_idx, col_name in enumerate(columns):
                value = row_data.get(col_name, "")
                if isinstance(value, float):
                    value = f"{value:.2f}"
                else:
                    value = str(value) if value is not None else ""
                
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                # Alternate row colors
                if row_idx % 2 == 1:
                    item.setBackground(QColor(15, 23, 42, 50))
                
                self.table.setItem(row_idx, col_idx, item)
        
        # Resize columns to content
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Update count
        self.row_count_label.setText(f"{len(data)} records")
    
    def filter_table(self, text):
        """Filter table rows based on search text."""
        text = text.lower()
        visible_count = 0
        
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            
            self.table.setRowHidden(row, not match)
            if match:
                visible_count += 1
        
        # Update count
        total = self.table.rowCount()
        if text:
            self.row_count_label.setText(f"Showing {visible_count} of {total} records")
        else:
            self.row_count_label.setText(f"{total} records")
    
    def clear_data(self):
        """Clear all data from the table."""
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.row_count_label.setText("0 records")
        self.search_input.clear()
