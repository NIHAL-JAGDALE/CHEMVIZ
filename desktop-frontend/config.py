"""
Configuration for the Desktop Application.
Matching web frontend design system.
"""

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

# Application Settings
APP_NAME = "CHEMVIZ - Equipment Visualizer"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Colors (matching web frontend premium design)
# NOTE: Use hex colors for matplotlib compatibility
COLORS = {
    # Primary colors
    "primary": "#6366f1",
    "primary_dark": "#4f46e5",
    "primary_light": "#818cf8",
    
    # Secondary colors
    "secondary": "#06b6d4",
    "secondary_dark": "#0891b2",
    
    # Accent colors
    "accent": "#f43f5e",
    "accent_light": "#fb7185",
    
    # Background colors - Dark Theme (hex for matplotlib)
    "bg_darker": "#020617",
    "bg_dark": "#0f172a",
    "bg_card": "#1e293b",
    "bg_glass": "#0f172acc",  # Hex with alpha
    "bg_glass_strong": "#0f172af2",
    
    # Background colors - Light Theme
    "bg_light": "#f1f5f9",
    "bg_card_light": "#ffffff",
    
    # Text colors - Dark Theme
    "text_primary": "#ffffff",
    "text_secondary": "#cbd5e1",
    "text_muted": "#94a3b8",
    
    # Text colors - Light Theme
    "text_primary_light": "#020617",
    "text_secondary_light": "#1e293b",
    "text_muted_light": "#475569",
    
    # Border colors (hex for matplotlib compatibility)
    "border": "#2d3748",  # Solid hex color
    "border_highlight": "#4a5568",
    "border_light": "#1a1a1a",
    
    # Status colors
    "success": "#10b981",
    "error": "#ef4444",
    "warning": "#f59e0b",
}

# QSS-specific colors (with rgba support for stylesheets only)
QSS_COLORS = {
    "border": "rgba(148, 163, 184, 0.1)",
    "border_highlight": "rgba(148, 163, 184, 0.2)",
    "border_light": "rgba(0, 0, 0, 0.1)",
    "bg_glass": "rgba(15, 23, 42, 0.8)",
    "bg_glass_strong": "rgba(15, 23, 42, 0.95)",
}

# Chart Colors (matching web frontend)
CHART_COLORS = [
    "#6366f1",  # Primary
    "#8b5cf6",  # Purple
    "#06b6d4",  # Cyan
    "#10b981",  # Green
    "#f59e0b",  # Amber
    "#ec4899",  # Pink
    "#f43f5e",  # Rose
    "#3b82f6",  # Blue
]

# Gradient definitions
GRADIENTS = {
    "primary": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366f1, stop:1 #8b5cf6)",
    "secondary": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3b82f6, stop:1 #06b6d4)",
    "accent": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ec4899, stop:1 #f43f5e)",
    "danger": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f43f5e, stop:1 #fb7185)",
}

# Animation durations (ms)
ANIMATIONS = {
    "fast": 150,
    "normal": 300,
    "slow": 600,
}

# Spacing
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "2xl": 48,
}

# Border radius
RADIUS = {
    "sm": 6,
    "md": 10,
    "lg": 16,
    "xl": 24,
    "full": 9999,
}
