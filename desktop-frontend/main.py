"""
Chemical Equipment Parameter Visualizer - Desktop Application
Main entry point for the PyQt5 desktop frontend.
Premium design matching web frontend.
"""
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSplitter, QFrame, QMessageBox, QFileDialog,
    QScrollArea, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap

from config import COLORS, GRADIENTS, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, RADIUS, SPACING
from api_client import api_client
from widgets import (
    LoginDialog, UploadWidget, DataTableWidget, 
    ChartsWidget, HistoryWidget
)


class DataLoaderThread(QThread):
    """Background thread for loading dataset data."""
    finished = pyqtSignal(dict, dict)
    error = pyqtSignal(str)
    
    def __init__(self, dataset_id):
        super().__init__()
        self.dataset_id = dataset_id
    
    def run(self):
        try:
            summary = api_client.get_dataset_summary(self.dataset_id)
            data = api_client.get_dataset_data(self.dataset_id)
            self.finished.emit(summary, data)
        except Exception as e:
            self.error.emit(str(e))


class SummaryCard(QFrame):
    """Premium summary card matching web frontend."""
    
    def __init__(self, value: str, label: str, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(180)
        self.setFixedHeight(100)
        self.setCursor(Qt.PointingHandCursor)
        self.setup_ui(value, label)
        self._apply_style()
    
    def _apply_style(self):
        self.setStyleSheet(f"""
            SummaryCard {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_highlight']};
                border-radius: {RADIUS['md']}px;
            }}
            SummaryCard:hover {{
                border-color: {COLORS['primary']};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def setup_ui(self, value: str, label: str):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        layout.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        text_label = QLabel(label.upper())
        text_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        text_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            letter-spacing: 0.5px;
        """)
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)
    
    def update_value(self, value: str, label: str):
        layout = self.layout()
        layout.itemAt(0).widget().setText(value)
        layout.itemAt(1).widget().setText(label.upper())


class UserProfileCard(QFrame):
    """User profile card matching web frontend sidebar."""
    
    clicked = pyqtSignal()
    
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(70)
        self.setup_ui()
        self._update_style(False)
    
    def _update_style(self, hovered):
        if hovered:
            self.setStyleSheet(f"""
                UserProfileCard {{
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                UserProfileCard {{
                    background: {COLORS['bg_card']};
                    border: 1px solid {COLORS['border_highlight']};
                    border-radius: 12px;
                }}
            """)
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        
        # Avatar
        avatar = QLabel(self.username[0].upper() if self.username else "U")
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFont(QFont("Segoe UI", 14, QFont.Bold))
        avatar.setStyleSheet(f"""
            background: {GRADIENTS['primary']};
            color: white;
            border-radius: 20px;
        """)
        layout.addWidget(avatar)
        
        # User info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        signed_in = QLabel("SIGNED IN AS")
        signed_in.setFont(QFont("Segoe UI", 8))
        signed_in.setStyleSheet(f"color: {COLORS['text_muted']}; letter-spacing: 0.5px;")
        info_layout.addWidget(signed_in)
        
        self.username_label = QLabel(self.username)
        self.username_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.username_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        info_layout.addWidget(self.username_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Settings icon
        settings = QLabel("⚙️")
        settings.setStyleSheet("font-size: 12px; opacity: 0.5;")
        layout.addWidget(settings)
    
    def set_username(self, username: str):
        self.username = username
        self.username_label.setText(username)
    
    def enterEvent(self, event):
        self._update_style(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._update_style(False)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class Sidebar(QFrame):
    """Premium sidebar matching web frontend."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(280)
        self.setup_ui()
        self._apply_style()
    
    def _apply_style(self):
        self.setStyleSheet(f"""
            Sidebar {{
                background: {COLORS['bg_glass_strong']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Logo
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()
        
        logo_icon = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Resize while keeping aspect ratio - Make it big!
            scaled_pixmap = pixmap.scaledToHeight(180, Qt.SmoothTransformation)
            logo_icon.setPixmap(scaled_pixmap)
        else:
            logo_icon.setText("⚗️")
            logo_icon.setStyleSheet("font-size: 64px;")
            
        logo_layout.addWidget(logo_icon)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)
        
        # User profile placeholder
        self.profile_placeholder = QWidget()
        self.profile_layout = QVBoxLayout(self.profile_placeholder)
        self.profile_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.profile_placeholder)
        
        # History widget placeholder
        self.history_placeholder = QWidget()
        self.history_layout = QVBoxLayout(self.history_placeholder)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.history_placeholder, 1)
        
        # Bottom buttons

        
        # Sign out button placeholder
        self.signout_placeholder = QWidget()
        self.signout_layout = QVBoxLayout(self.signout_placeholder)
        self.signout_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.signout_placeholder)
    
    def set_profile(self, profile_widget):
        while self.profile_layout.count():
            item = self.profile_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.profile_layout.addWidget(profile_widget)
    
    def set_history(self, history_widget):
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.history_layout.addWidget(history_widget)
    
    def set_signout(self, signout_widget):
        while self.signout_layout.count():
            item = self.signout_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.signout_layout.addWidget(signout_widget)


class MainWindow(QMainWindow):
    """Main application window with premium design."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.current_dataset = None
        self.loader_thread = None
        self.is_showing_dataset = False
        
        self._apply_global_style()
        self.setup_ui()
        self.refresh_datasets()
    
    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg_darker']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QMessageBox {{
                background-color: {COLORS['bg_card']};
            }}
            QMessageBox QLabel {{
                color: {COLORS['text_primary']};
            }}
            QMessageBox QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
            
            /* Global Scrollbar Styles */
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border_highlight']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['primary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: transparent;
                height: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {COLORS['border_highlight']};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {COLORS['primary']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                background: none;
                width: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        
        # User profile
        self.user_profile = UserProfileCard(api_client.username or "User")
        self.sidebar.set_profile(self.user_profile)
        
        # History widget
        self.history_widget = HistoryWidget()
        self.history_widget.dataset_selected.connect(self.on_dataset_selected)
        self.history_widget.dataset_deleted.connect(self.on_dataset_deleted)
        self.sidebar.set_history(self.history_widget)
        
        # Sign out button
        self.logout_btn = QPushButton("Sign Out")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                padding: 12px;
                color: {COLORS['text_secondary']};
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.05);
                border-color: {COLORS['primary']};
                color: {COLORS['primary']};
            }}
        """)
        self.logout_btn.clicked.connect(self.logout)
        self.sidebar.set_signout(self.logout_btn)
        
        main_layout.addWidget(self.sidebar)
        
        # Main content area
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background: {COLORS['bg_darker']};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(SPACING['xl'], SPACING['xl'], SPACING['xl'], SPACING['xl'])
        content_layout.setSpacing(SPACING['lg'])
        
        # Stacked widget for different views
        self.content_stack = QStackedWidget()
        
        # Dashboard view (upload)
        self.dashboard_view = self.create_dashboard_view()
        self.content_stack.addWidget(self.dashboard_view)
        
        # Dataset view (charts + table)
        self.dataset_view = self.create_dataset_view()
        self.content_stack.addWidget(self.dataset_view)
        
        content_layout.addWidget(self.content_stack)
        main_layout.addWidget(content_widget, 1)
    
    def create_dashboard_view(self):
        """Create the dashboard/upload view."""
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['xl'])
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Equipment Analytics Dashboard")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Upload widget
        self.upload_widget = UploadWidget()
        self.upload_widget.upload_success.connect(self.on_upload_success)
        layout.addWidget(self.upload_widget)
        
        # Welcome message
        welcome_container = QWidget()
        welcome_layout = QVBoxLayout(welcome_container)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_layout.setSpacing(SPACING['md'])
        
        welcome_icon = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaledToHeight(64, Qt.SmoothTransformation)
            welcome_icon.setPixmap(scaled_pixmap)
        else:
            welcome_icon.setText("📊")
            welcome_icon.setStyleSheet("font-size: 64px; opacity: 0.5;")
        welcome_icon.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_icon)
        
        welcome_title = QLabel("Welcome to CHEMVIZ")
        welcome_title.setFont(QFont("Segoe UI", 18, QFont.Medium))
        welcome_title.setStyleSheet(f"color: {COLORS['text_secondary']};")
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_title)
        
        welcome_text = QLabel("Select a dataset from the sidebar or upload a new CSV to get started.")
        welcome_text.setFont(QFont("Segoe UI", 11))
        welcome_text.setStyleSheet(f"color: {COLORS['text_muted']};")
        welcome_text.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_text)
        
        layout.addWidget(welcome_container)
        layout.addStretch()
        
        return view
    
    def create_dataset_view(self):
        """Create the dataset detail view."""
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['lg'])
        
        # Header (Fixed at top)
        header = QHBoxLayout()
        
        # Left side - back button and title
        left_header = QVBoxLayout()
        
        self.back_btn = QPushButton("← Back to Dashboard")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                padding: 8px 16px;
                color: {COLORS['text_secondary']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {COLORS['primary']};
                border-color: {COLORS['primary']};
                color: white;
            }}
        """)
        self.back_btn.clicked.connect(self.show_dashboard)
        left_header.addWidget(self.back_btn, 0, Qt.AlignLeft)
        
        self.dataset_title = QLabel("Dataset Details")
        self.dataset_title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.dataset_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        left_header.addWidget(self.dataset_title)
        
        self.dataset_meta = QLabel("Uploaded on...")
        self.dataset_meta.setFont(QFont("Segoe UI", 10))
        self.dataset_meta.setStyleSheet(f"color: {COLORS['text_muted']};")
        left_header.addWidget(self.dataset_meta)
        
        header.addLayout(left_header)
        header.addStretch()
        
        # Right side - action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACING['md'])
        
        self.delete_btn = QPushButton("🗑️ Delete Dataset")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background: {GRADIENTS['danger']};
                color: white;
                border: none;
                border-radius: {RADIUS['md']}px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #dc2626;
            }}
        """)
        self.delete_btn.clicked.connect(self.delete_current_dataset)
        btn_layout.addWidget(self.delete_btn)
        
        self.download_btn = QPushButton("📥 Download PDF Report")
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background: {GRADIENTS['primary']};
                color: white;
                border: none;
                border-radius: {RADIUS['md']}px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
        """)
        self.download_btn.clicked.connect(self.download_report)
        btn_layout.addWidget(self.download_btn)
        
        header.addLayout(btn_layout)
        layout.addLayout(header)
        
        # Scrollable content area
        page_scroll = QScrollArea()
        page_scroll.setWidgetResizable(True)
        # Transparent background to match theme
        page_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 10, 0) # Small padding for scrollbar
        scroll_layout.setSpacing(SPACING['lg'])
        
        # Summary cards
        self.summary_scroll = QScrollArea()
        self.summary_scroll.setWidgetResizable(True)
        self.summary_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.summary_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.summary_scroll.setFixedHeight(120)
        self.summary_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        self.summary_container = QWidget()
        self.summary_layout = QHBoxLayout(self.summary_container)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)
        self.summary_layout.setSpacing(SPACING['md'])
        self.summary_layout.addStretch()
        
        self.summary_scroll.setWidget(self.summary_container)
        scroll_layout.addWidget(self.summary_scroll)
        
        # Charts
        self.charts_widget = ChartsWidget()
        scroll_layout.addWidget(self.charts_widget)
        
        # Data table
        self.table_widget = DataTableWidget()
        self.table_widget.setMinimumHeight(600)  # Ensure table is visible and scrollable
        scroll_layout.addWidget(self.table_widget)
        
        page_scroll.setWidget(scroll_content)
        layout.addWidget(page_scroll)
        
        return view
    
    def show_dashboard(self):
        """Switch to dashboard view."""
        self.is_showing_dataset = False
        self.content_stack.setCurrentIndex(0)
        self.current_dataset = None
    
    def show_dataset_view(self):
        """Switch to dataset view."""
        self.is_showing_dataset = True
        self.content_stack.setCurrentIndex(1)
    
    def update_summary_cards(self, summary: dict):
        """Update summary cards with data."""
        # Clear existing cards
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Total count card
        total = summary.get('total_count', 0)
        card = SummaryCard(str(total), "Total Records")
        self.summary_layout.addWidget(card)
        
        # Average cards
        for param, value in summary.get('averages', {}).items():
            label = f"Avg {param.replace('_', ' ').title()}"
            card = SummaryCard(f"{value:.2f}", label)
            self.summary_layout.addWidget(card)
        
        self.summary_layout.addStretch()
    
    def refresh_datasets(self):
        """Refresh the datasets list."""
        try:
            datasets = api_client.get_datasets()
            self.history_widget.load_datasets(datasets)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load datasets: {e}")
    
    def on_dataset_selected(self, dataset: dict):
        """Handle dataset selection."""
        self.current_dataset = dataset
        self.show_dataset_view()
        
        # Update header
        self.dataset_title.setText(dataset.get('filename', 'Dataset Details'))
        
        from datetime import datetime
        uploaded_at = dataset.get('uploaded_at', '')
        try:
            dt = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
            date_str = dt.strftime('%b %d, %Y at %H:%M')
        except:
            date_str = uploaded_at[:16] if uploaded_at else ''
        self.dataset_meta.setText(f"Uploaded on {date_str}")
        
        # Load data in background
        self.loader_thread = DataLoaderThread(dataset['id'])
        self.loader_thread.finished.connect(self.on_data_loaded)
        self.loader_thread.error.connect(lambda e: QMessageBox.warning(self, "Error", e))
        self.loader_thread.start()
    
    def on_data_loaded(self, summary_response: dict, data_response: dict):
        """Handle loaded dataset data."""
        summary = summary_response.get('summary', {})
        
        # Update UI
        self.update_summary_cards(summary)
        self.charts_widget.update_charts(summary)
        self.table_widget.load_data(
            data_response.get('columns', []),
            data_response.get('data', [])
        )
    
    def on_upload_success(self, data: dict):
        """Handle successful upload."""
        self.refresh_datasets()
        
        # Navigate to the new dataset
        QTimer.singleShot(500, lambda: self.on_dataset_selected({
            'id': data.get('dataset_id'),
            'filename': data.get('filename'),
            'uploaded_at': data.get('uploaded_at', ''),
            'total_count': data.get('summary', {}).get('total_count', 0)
        }))
    
    def on_dataset_deleted(self, dataset: dict):
        """Handle dataset deletion from sidebar."""
        try:
            api_client.delete_dataset(dataset['id'])
            self.refresh_datasets()
            
            # If viewing the deleted dataset, go back to dashboard
            if self.current_dataset and self.current_dataset['id'] == dataset['id']:
                self.show_dashboard()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete dataset: {e}")
    
    def delete_current_dataset(self):
        """Delete the currently viewed dataset."""
        if not self.current_dataset:
            return
        
        reply = QMessageBox.question(
            self, 'Delete Dataset',
            f'Are you sure you want to delete "{self.current_dataset["filename"]}"?\n\nThis action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                api_client.delete_dataset(self.current_dataset['id'])
                self.refresh_datasets()
                self.show_dashboard()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete dataset: {e}")
    
    def download_report(self):
        """Download PDF report for current dataset."""
        if not self.current_dataset:
            return
        
        filename = self.current_dataset.get('filename', 'report').replace('.csv', '')
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            f"{filename}_report.pdf",
            "PDF Files (*.pdf)"
        )
        
        if save_path:
            try:
                api_client.download_report(self.current_dataset['id'], save_path)
                QMessageBox.information(self, "Success", f"Report saved to:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to download report: {e}")
    
    def logout(self):
        """Log out and return to login screen."""
        api_client.logout()
        self.close()
        
        # Show login dialog again
        login = LoginDialog()
        if login.exec_() == LoginDialog.Accepted:
            window = MainWindow()
            window.show()
            window.user_profile.set_username(api_client.username)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(COLORS['bg_darker']))
    palette.setColor(QPalette.WindowText, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.Base, QColor(COLORS['bg_card']))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS['bg_dark']))
    palette.setColor(QPalette.ToolTipBase, QColor(COLORS['bg_card']))
    palette.setColor(QPalette.ToolTipText, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.Text, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.Button, QColor(COLORS['bg_card']))
    palette.setColor(QPalette.ButtonText, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.Highlight, QColor(COLORS['primary']))
    palette.setColor(QPalette.HighlightedText, QColor('white'))
    app.setPalette(palette)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Show login dialog
    login = LoginDialog()
    if login.exec_() != LoginDialog.Accepted:
        sys.exit(0)
    
    # Show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
