"""
History Widget for displaying recent datasets.
Premium design matching web frontend Sidebar.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame,
    QLabel, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect,
    QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QFontMetrics
from datetime import datetime

from config import COLORS, RADIUS, SPACING


class ElidedLabel(QLabel):
    """Label that elides text when it exceeds width."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._full_text = text
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
    
    def setText(self, text):
        self._full_text = text
        self.update_text()
    
    def resizeEvent(self, event):
        self.update_text()
        super().resizeEvent(event)
    
    def update_text(self):
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self._full_text, Qt.ElideRight, self.width())
        super().setText(elided)


class DatasetItem(QFrame):
    """Individual dataset item in the history list."""
    
    clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)
    
    def __init__(self, dataset, parent=None):
        super().__init__(parent)
        self.dataset = dataset
        self.setFixedHeight(70)
        self.setCursor(Qt.PointingHandCursor)
        self.setup_ui()
        self._update_style(False)
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 16, 10)
        layout.setSpacing(10)
        
        # File icon
        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon)
        
        # Content
        content = QVBoxLayout()
        content.setSpacing(2)
        
        # Filename
        self.name_label = ElidedLabel(self.dataset.get('filename', 'Unknown'))
        self.name_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        self.name_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        content.addWidget(self.name_label)
        
        # Meta info
        uploaded_at = self.dataset.get('uploaded_at', '')
        try:
            dt = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
            date_str = dt.strftime('%b %d, %H:%M')
        except:
            date_str = uploaded_at[:16] if uploaded_at else ''
        
        total = self.dataset.get('total_count', '?')
        meta_text = f"{date_str} • {total} records"
        
        self.meta_label = ElidedLabel(meta_text)
        self.meta_label.setFont(QFont("Segoe UI", 9))
        self.meta_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        content.addWidget(self.meta_label)
        
        layout.addLayout(content, 1)
        
        # Delete button
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setFixedSize(28, 28)
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                font-size: 14px;
                border-radius: 14px;
            }}
            QPushButton:hover {{
                background: rgba(244, 63, 94, 0.2);
            }}
        """)
        self.delete_btn.clicked.connect(self._on_delete)
        self.delete_btn.hide()
        layout.addWidget(self.delete_btn)
    
    def _update_style(self, hovered):
        if hovered:
            self.setStyleSheet(f"""
                DatasetItem {{
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid {COLORS['border_highlight']};
                    border-radius: {RADIUS['md']}px;
                    border-left: 4px solid {COLORS['primary']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                DatasetItem {{
                    background: transparent;
                    border: 1px solid transparent;
                    border-radius: {RADIUS['md']}px;
                }}
            """)
    
    def enterEvent(self, event):
        self._update_style(True)
        self.delete_btn.show()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._update_style(False)
        self.delete_btn.hide()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.dataset)
        super().mousePressEvent(event)
    
    def _on_delete(self):
        self.delete_clicked.emit(self.dataset)
    
    def set_selected(self, selected):
        if selected:
            self.setStyleSheet(f"""
                DatasetItem {{
                    background: rgba(99, 102, 241, 0.15);
                    border: 1px solid {COLORS['primary']};
                    border-radius: {RADIUS['md']}px;
                    border-left: 4px solid {COLORS['primary']};
                }}
            """)
        else:
            self._update_style(False)


class HistoryWidget(QWidget):
    """Widget for displaying and selecting recent datasets."""
    
    dataset_selected = pyqtSignal(dict)
    dataset_deleted = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.datasets = []
        self.dataset_items = []
        self.selected_item = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['sm'])
        
        # Title
        title = QLabel("RECENT DATASETS")
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-weight: 700;
            letter-spacing: 0.8px;
            padding-bottom: 8px;
        """)
        layout.addWidget(title)
        
        # Scroll area for datasets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border_highlight']};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['primary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(4)
        self.scroll_layout.addStretch()
        
        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)
        
        # Empty state
        self.empty_label = QLabel("No datasets uploaded yet")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setFont(QFont("Segoe UI", 10))
        self.empty_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            padding: 20px;
        """)
        self.empty_label.hide()
        layout.addWidget(self.empty_label)
    
    def load_datasets(self, datasets: list):
        """Load datasets into the list."""
        self.datasets = datasets
        self.dataset_items = []
        self.selected_item = None
        
        # Clear existing items
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not datasets:
            self.empty_label.show()
            return
        
        self.empty_label.hide()
        
        # Add dataset items
        for dataset in datasets:
            item = DatasetItem(dataset)
            item.clicked.connect(self.on_item_clicked)
            item.delete_clicked.connect(self.on_delete_clicked)
            self.dataset_items.append(item)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, item)
    
    def on_item_clicked(self, dataset):
        """Handle dataset selection."""
        # Update selection state
        for item in self.dataset_items:
            if item.dataset['id'] == dataset['id']:
                item.set_selected(True)
                self.selected_item = item
            else:
                item.set_selected(False)
        
        self.dataset_selected.emit(dataset)
    
    def on_delete_clicked(self, dataset):
        """Handle delete button click."""
        reply = QMessageBox.question(
            self, 'Delete Dataset',
            f'Are you sure you want to delete "{dataset["filename"]}"?\n\nThis action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.dataset_deleted.emit(dataset)
    
    def select_first(self):
        """Select the first dataset if available."""
        if self.dataset_items:
            self.on_item_clicked(self.dataset_items[0].dataset)
    
    def refresh_after_delete(self, deleted_id):
        """Refresh the list after a dataset is deleted."""
        self.datasets = [d for d in self.datasets if d['id'] != deleted_id]
        self.load_datasets(self.datasets)
