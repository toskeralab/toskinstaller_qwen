"""
Página 7 - Atalhos e Configurações
Criação de atalhos, pasta de destino, arquitetura
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QComboBox, 
    QGroupBox, QLineEdit, QHBoxLayout
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from ...core.logger import get_logger

logger = get_logger(__name__)


class ShortcutsPage(QWidget):
    """Página 7 - Configuração de atalhos e instalações"""
    
    shortcuts_configured = Signal(dict)
    validation_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = {
            'create_desktop': True,
            'create_start_menu': True,
            'architecture': 'x64'
        }
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel("Atalhos e Instalação")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        desc = QLabel(
            "Configure onde e como o aplicativo será instalado."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Atalhos
        shortcut_group = QGroupBox("Atalhos")
        shortcut_layout = QVBoxLayout(shortcut_group)
        
        self.desktop_cb = QCheckBox("Criar atalho na Área de Trabalho")
        self.desktop_cb.setChecked(True)
        self.desktop_cb.stateChanged.connect(self._on_changed)
        shortcut_layout.addWidget(self.desktop_cb)
        
        self.start_cb = QCheckBox("Criar atalho no Menu Iniciar")
        self.start_cb.setChecked(True)
        self.start_cb.stateChanged.connect(self._on_changed)
        shortcut_layout.addWidget(self.start_cb)
        
        layout.addWidget(shortcut_group)
        
        # Arquitetura
        arch_group = QGroupBox("Arquitetura")
        arch_layout = QHBoxLayout(arch_group)
        
        self.arch_combo = QComboBox()
        self.arch_combo.addItems(["x64 (64-bit)", "x86 (32-bit)", "ARM64"])
        self.arch_combo.currentIndexChanged.connect(self._on_changed)
        arch_layout.addWidget(self.arch_combo)
        
        layout.addWidget(arch_group)
        
        # Pasta de instalação
        folder_group = QGroupBox("Pasta de Instalação")
        folder_layout = QVBoxLayout(folder_group)
        
        folder_line = QHBoxLayout()
        self.folder_edit = QLineEdit("C:\\Program Files\\MyApp")
        folder_line.addWidget(self.folder_edit)
        
        browse_btn = QPushButton("Procurar...")
        folder_line.addWidget(browse_btn)
        
        folder_layout.addLayout(folder_line)
        layout.addWidget(folder_group)
        
        layout.addStretch()
        
    def _on_changed(self):
        self._config['create_desktop'] = self.desktop_cb.isChecked()
        self._config['create_start_menu'] = self.start_cb.isChecked()
        
        arch_map = {0: 'x64', 1: 'x86', 2: 'ARM64'}
        self._config['architecture'] = arch_map.get(self.arch_combo.currentIndex(), 'x64')
        
        self.shortcuts_configured.emit(self._config)
        self.validation_changed.emit(True)
        
    def validate(self) -> bool:
        return True
        
    def get_data(self) -> dict:
        return self._config
        
    def initialize(self, config: dict):
        if 'create_desktop' in config:
            self.desktop_cb.setChecked(config['create_desktop'])
        if 'create_start_menu' in config:
            self.start_cb.setChecked(config['create_start_menu'])
