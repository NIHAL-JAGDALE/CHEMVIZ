"""
Package initialization for widgets.
"""
from .login_dialog import LoginDialog
from .upload_widget import UploadWidget
from .data_table import DataTableWidget
from .charts_widget import ChartsWidget
from .history_widget import HistoryWidget

__all__ = [
    'LoginDialog',
    'UploadWidget',
    'DataTableWidget',
    'ChartsWidget',
    'HistoryWidget'
]
