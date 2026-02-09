"""
Login Dialog for authentication.
Premium design matching web frontend AuthPage.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame,
    QStackedWidget, QWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QPen, QLinearGradient, QPixmap
import os

from api_client import api_client
from config import COLORS, GRADIENTS, SPACING, RADIUS, QSS_COLORS


class AnimatedCircle(QWidget):
    """Animated background circle for visual effect."""
    
    def __init__(self, color, size, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.color.setAlpha(100)
        self.setFixedSize(size, size)
        self._offset = 0
        
        # Create floating animation
        self.anim = QPropertyAnimation(self, b"offset")
        self.anim.setDuration(4000)
        self.anim.setStartValue(0)
        self.anim.setEndValue(20)
        self.anim.setEasingCurve(QEasingCurve.InOutSine)
        self.anim.setLoopCount(-1)
        self.anim.start()
    
    @pyqtProperty(int)
    def offset(self):
        return self._offset
    
    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, self._offset, self.width(), self.height() - 40)


class GradientButton(QPushButton):
    """Custom gradient button matching web frontend."""
    
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setMinimumHeight(44)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()
    
    def _update_style(self):
        if self.primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {GRADIENTS['primary']};
                    color: white;
                    border: none;
                    border-radius: {RADIUS['md']}px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {GRADIENTS['primary']};
                }}
                QPushButton:pressed {{
                    background: {COLORS['primary_dark']};
                }}
                QPushButton:disabled {{
                    background: #4a4a6a;
                    color: #888;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {COLORS['text_secondary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: {RADIUS['md']}px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: rgba(99, 102, 241, 0.1);
                    border-color: {COLORS['primary']};
                    color: {COLORS['primary']};
                }}
            """)


class ModernLineEdit(QLineEdit):
    """Modern styled line edit matching web frontend."""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(42)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                padding: 10px 14px;
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                background-color: #0f172a;
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """)


class AuthTab(QPushButton):
    """Tab button for auth forms."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._active = False
        self.setCheckable(True)
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10, QFont.Medium))
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()
    
    def setActive(self, active):
        self._active = active
        self.setChecked(active)
        self._update_style()
    
    def _update_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['bg_card']};
                    color: {COLORS['text_primary']};
                    border: none;
                    border-radius: {RADIUS['sm']}px;
                    padding: 10px;
                    font-weight: 600;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {COLORS['text_secondary']};
                    border: none;
                    border-radius: {RADIUS['sm']}px;
                    padding: 10px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    color: {COLORS['text_primary']};
                }}
            """)


class LoginDialog(QDialog):
    """Premium login dialog matching web frontend design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CHEMVIZ - Login")
        self.setFixedWidth(460)
        self.setFixedHeight(550)  # Initial small size for login
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        # Use solid background - no transparency
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_card']};
                border-radius: {RADIUS['xl']}px;
            }}
        """)
        self.is_login_mode = True
        self.setup_ui()
        
        # Center on screen
        self.center_on_screen()
    
    def center_on_screen(self):
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main card container with SOLID background
        self.card = QFrame()
        self.card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['xl']}px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(36, 24, 36, 28)
        card_layout.setSpacing(14)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_muted']};
                border: none;
                font-size: 16px;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                color: {COLORS['text_primary']};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        close_btn.setCursor(Qt.PointingHandCursor)
        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        card_layout.addLayout(close_layout)
        
        # Logo section
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_layout.setSpacing(8)
        
        # Load logo image
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaledToWidth(120, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("⚗️ CHEMVIZ")
            logo_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
            logo_label.setStyleSheet(f"color: {COLORS['primary']};")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)
        
        subtitle = QLabel("Equipment Analytics Platform")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']};")
        subtitle.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(subtitle)
        
        card_layout.addLayout(logo_layout)
        card_layout.addSpacing(6)
        
        # Auth tabs
        tabs_container = QFrame()
        tabs_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_dark']};
                border-radius: {RADIUS['md']}px;
                padding: 4px;
            }}
        """)
        tabs_layout = QHBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(4, 4, 4, 4)
        tabs_layout.setSpacing(4)
        
        self.login_tab = AuthTab("Sign In")
        self.login_tab.setActive(True)
        self.login_tab.clicked.connect(lambda: self.switch_mode(True))
        tabs_layout.addWidget(self.login_tab)
        
        self.register_tab = AuthTab("Sign Up")
        self.register_tab.clicked.connect(lambda: self.switch_mode(False))
        tabs_layout.addWidget(self.register_tab)
        
        card_layout.addWidget(tabs_container)
        
        # Error/Success message
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setMinimumHeight(40)
        self.message_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: {COLORS['accent_light']};
                padding: 10px;
                border-radius: {RADIUS['md']}px;
                font-size: 12px;
            }}
        """)
        self.message_label.hide()
        card_layout.addWidget(self.message_label)
        
        # Stacked widget for forms
        self.form_stack = QStackedWidget()
        
        # Login form
        login_form = QWidget()
        login_layout = QVBoxLayout(login_form)
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setSpacing(16)
        
        # Username field
        username_container = QVBoxLayout()
        username_container.setSpacing(6)
        username_container.setContentsMargins(0, 0, 0, 0)
        username_label = QLabel("USERNAME")
        username_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding-left: 4px;
                background: transparent;
            }}
        """)
        username_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        username_container.addWidget(username_label)
        self.username_input = ModernLineEdit("Enter your username")
        username_container.addWidget(self.username_input)
        login_layout.addLayout(username_container)
        
        # Password field
        password_container = QVBoxLayout()
        password_container.setSpacing(6)
        password_container.setContentsMargins(0, 0, 0, 0)
        password_label = QLabel("PASSWORD")
        password_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding-left: 4px;
                background: transparent;
            }}
        """)
        password_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        password_container.addWidget(password_label)
        self.password_input = ModernLineEdit("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_container.addWidget(self.password_input)
        login_layout.addLayout(password_container)
        
        # Login button
        self.login_button = GradientButton("🔐  Sign In", primary=True)
        self.login_button.clicked.connect(self.handle_login)
        login_layout.addWidget(self.login_button)
        
        self.form_stack.addWidget(login_form)
        
        # Register form
        register_form = QWidget()
        register_layout = QVBoxLayout(register_form)
        register_layout.setContentsMargins(0, 0, 0, 0)
        register_layout.setSpacing(12)
        
        # Register username
        reg_username_container = QVBoxLayout()
        reg_username_container.setSpacing(8)
        reg_username_container.setContentsMargins(0, 0, 0, 0)
        reg_username_label = QLabel("USERNAME")
        reg_username_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding-left: 4px;
                background: transparent;
            }}
        """)
        reg_username_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        reg_username_container.addWidget(reg_username_label)
        self.reg_username_input = ModernLineEdit("Choose a username")
        reg_username_container.addWidget(self.reg_username_input)
        register_layout.addLayout(reg_username_container)
        
        # Email
        email_container = QVBoxLayout()
        email_container.setSpacing(8)
        email_container.setContentsMargins(0, 0, 0, 0)
        email_label = QLabel("EMAIL")
        email_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding-left: 4px;
                background: transparent;
            }}
        """)
        email_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        email_container.addWidget(email_label)
        self.email_input = ModernLineEdit("Enter your email")
        email_container.addWidget(self.email_input)
        register_layout.addLayout(email_container)
        
        # Register password
        reg_password_container = QVBoxLayout()
        reg_password_container.setSpacing(8)
        reg_password_container.setContentsMargins(0, 0, 0, 0)
        reg_password_label = QLabel("PASSWORD")
        reg_password_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding-left: 4px;
                background: transparent;
            }}
        """)
        reg_password_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        reg_password_container.addWidget(reg_password_label)
        self.reg_password_input = ModernLineEdit("Create a password (min 6 chars)")
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        reg_password_container.addWidget(self.reg_password_input)
        register_layout.addLayout(reg_password_container)
        
        # Confirm password
        confirm_container = QVBoxLayout()
        confirm_container.setSpacing(8)
        confirm_container.setContentsMargins(0, 0, 0, 0)
        confirm_label = QLabel("CONFIRM PASSWORD")
        confirm_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding-left: 4px;
                background: transparent;
            }}
        """)
        confirm_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        confirm_container.addWidget(confirm_label)
        self.confirm_password_input = ModernLineEdit("Confirm your password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        confirm_container.addWidget(self.confirm_password_input)
        register_layout.addLayout(confirm_container)
        
        # Register button
        self.register_button = GradientButton("🚀  Create Account", primary=True)
        self.register_button.clicked.connect(self.handle_register)
        register_layout.addWidget(self.register_button)
        
        self.form_stack.addWidget(register_form)
        
        card_layout.addWidget(self.form_stack)
        
        # Footer
        footer = QLabel()
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px;")
        footer.setText("Chemical Equipment Data Analytics Platform")
        card_layout.addWidget(footer)
        
        main_layout.addWidget(self.card)
        
        # Connect Enter key
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.confirm_password_input.returnPressed.connect(self.handle_register)
    
    def switch_mode(self, is_login):
        self.is_login_mode = is_login
        self.login_tab.setActive(is_login)
        self.register_tab.setActive(not is_login)
        self.form_stack.setCurrentIndex(0 if is_login else 1)
        self.message_label.hide()
        
        # Resize window based on mode
        if is_login:
            self.setFixedHeight(550)
        else:
            self.setFixedHeight(750)
            
        self.center_on_screen()
    
    def show_message(self, text, is_error=True):
        color = COLORS['accent_light'] if is_error else COLORS['success']
        bg_color = "rgba(244, 63, 94, 0.1)" if is_error else "rgba(16, 185, 129, 0.1)"
        self.message_label.setStyleSheet(f"""
            QLabel {{
                background: {bg_color};
                color: {color};
                padding: 10px;
                border-radius: {RADIUS['md']}px;
                font-size: 12px;
                border: 1px solid {color};
            }}
        """)
        self.message_label.setText(text)
        self.message_label.show()
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_message("Please enter both username and password")
            return
        
        try:
            self.login_button.setEnabled(False)
            self.login_button.setText("Signing in...")
            
            api_client.login(username, password)
            self.accept()
            
        except Exception as e:
            self.show_message(str(e))
        finally:
            self.login_button.setEnabled(True)
            self.login_button.setText("🔐  Sign In")
    
    def handle_register(self):
        username = self.reg_username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.reg_password_input.text()
        confirm = self.confirm_password_input.text()
        
        if not all([username, email, password, confirm]):
            self.show_message("Please fill in all fields")
            return
        
        if password != confirm:
            self.show_message("Passwords do not match")
            return
        
        if len(password) < 6:
            self.show_message("Password must be at least 6 characters")
            return
        
        try:
            self.register_button.setEnabled(False)
            self.register_button.setText("Creating account...")
            
            api_client.register(username, email, password)
            self.accept()
            
        except Exception as e:
            self.show_message(str(e))
        finally:
            self.register_button.setEnabled(True)
            self.register_button.setText("🚀  Create Account")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.pos()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPos() - self.drag_pos)
