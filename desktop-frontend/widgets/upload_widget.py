"""
Upload Widget for CSV file selection and upload.
Premium design matching web frontend FileUploader.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QProgressBar, QMessageBox,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QDragEnterEvent, QDropEvent

from api_client import api_client
from config import COLORS, GRADIENTS, RADIUS, SPACING


class UploadWorker(QThread):
    """Background worker for file upload."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            result = api_client.upload_dataset(self.file_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class UploadZone(QFrame):
    """Drag and drop upload zone with premium styling."""
    
    file_dropped = pyqtSignal(str)
    browse_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        self.is_drag_over = False
        self._update_style()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(SPACING['md'])
        
        # Upload icon
        self.icon = QLabel("📤")
        self.icon.setStyleSheet("font-size: 48px; background: transparent; border: none;")
        self.icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon)
        
        # Main text
        self.main_text = QLabel("Drag & drop a CSV file here")
        self.main_text.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.main_text.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent; border: none;")
        self.main_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.main_text)
        
        # Subtitle
        self.subtitle = QLabel("or click to browse files")
        self.subtitle.setFont(QFont("Segoe UI", 10))
        self.subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none;")
        self.subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle)
        
        # Hint
        hint = QLabel("Supports any CSV file format")
        hint.setFont(QFont("Segoe UI", 9))
        hint.setStyleSheet(f"color: {COLORS['text_muted']}; opacity: 0.7; background: transparent; border: none;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
    
    def _update_style(self):
        if self.is_drag_over:
            self.setStyleSheet(f"""
                UploadZone {{
                    background: rgba(99, 102, 241, 0.15);
                    border: 2px dashed {COLORS['primary']};
                    border-radius: {RADIUS['lg']}px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                UploadZone {{
                    background: {COLORS['bg_card']};
                    border: 2px dashed {COLORS['border_highlight']};
                    border-radius: {RADIUS['lg']}px;
                }}
                UploadZone:hover {{
                    border-color: {COLORS['primary']};
                    background: rgba(99, 102, 241, 0.05);
                }}
            """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toLocalFile().endswith('.csv'):
                event.acceptProposedAction()
                self.is_drag_over = True
                self._update_style()
    
    def dragLeaveEvent(self, event):
        self.is_drag_over = False
        self._update_style()
    
    def dropEvent(self, event: QDropEvent):
        self.is_drag_over = False
        self._update_style()
        
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.csv'):
                self.file_dropped.emit(file_path)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.browse_clicked.emit()
        super().mousePressEvent(event)
    
    def set_uploading(self, filename):
        """Update display for uploading state."""
        self.icon.setText("⏳")
        self.main_text.setText(f"Uploading: {filename}")
        self.subtitle.setText("Please wait...")
    
    def set_success(self, filename):
        """Update display for success state."""
        self.icon.setText("✅")
        self.main_text.setText(f"Successfully uploaded!")
        self.subtitle.setText(filename)
        self.subtitle.setStyleSheet(f"color: {COLORS['success']}; background: transparent; border: none;")
    
    def reset(self):
        """Reset to default state."""
        self.icon.setText("📤")
        self.main_text.setText("Drag & drop a CSV file here")
        self.subtitle.setText("or click to browse files")
        self.subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none;")


class UploadWidget(QWidget):
    """Widget for uploading CSV files with premium styling."""
    
    upload_success = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['md'])
        
        # Section title
        title_row = QHBoxLayout()
        title = QLabel("Upload New Dataset")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)
        
        # Upload zone
        self.upload_zone = UploadZone()
        self.upload_zone.setCursor(Qt.PointingHandCursor)
        self.upload_zone.file_dropped.connect(self.upload_file)
        self.upload_zone.browse_clicked.connect(self.browse_file)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.upload_zone.setGraphicsEffect(shadow)
        
        layout.addWidget(self.upload_zone)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {GRADIENTS['primary']};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            self.upload_file(file_path)
    
    def upload_file(self, file_path: str):
        filename = file_path.split('/')[-1].split('\\')[-1]
        
        self.upload_zone.set_uploading(filename)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.show()
        
        self.worker = UploadWorker(file_path)
        self.worker.finished.connect(self.on_upload_success)
        self.worker.error.connect(self.on_upload_error)
        self.worker.start()
    
    def on_upload_success(self, data: dict):
        self.progress_bar.hide()
        self.upload_zone.set_success(data.get('filename', 'File'))
        self.upload_success.emit(data)
        
        # Reset after delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, self.upload_zone.reset)
    
    def on_upload_error(self, error: str):
        self.progress_bar.hide()
        self.upload_zone.reset()
        QMessageBox.critical(self, "Upload Failed", error)
