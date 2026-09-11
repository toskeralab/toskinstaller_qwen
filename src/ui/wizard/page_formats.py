"""
Página 4 - Formatos do Pacote
Seleção múltipla de formatos de saída (.EXE, .MSI, Portable)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QGroupBox, QPushButton
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from ...core.logger import get_logger

logger = get_logger(__name__)


class PackageFormatsPage(QWidget):
    """Página 4 - Seleção de formatos de pacote"""
    
    formats_selected = Signal(list)
    validation_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._formats = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel("Formatos de Saída")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        desc = QLabel(
            "Selecione um ou mais formatos para o pacote final.\n"
            "Você pode gerar múltiplos formatos simultaneamente."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Grupo de formatos
        format_group = QGroupBox("Formatos Disponíveis")
        format_layout = QVBoxLayout(format_group)
        
        self.format_checks = {}
        
        formats = [
            ("exe_installer", "Instalador .EXE (Inno Setup)", 
             "Criador de instalador executável com wizard personalizado"),
            ("msi_installer", "Instalador .MSI (Windows Installer)",
             "Pacote Windows Installer padrão (requer WiX Toolset)"),
            ("portable", "Portable (Descompactador)",
             "Extrai o app em uma pasta sem instalação no sistema"),
        ]
        
        for key, label, description in formats:
            cb = QCheckBox(label)
            cb.setProperty("format_key", key)
            cb.setToolTip(description)
            cb.stateChanged.connect(self._on_format_changed)
            format_layout.addWidget(cb)
            self.format_checks[key] = cb
            
        layout.addWidget(format_group)
        
        # Aviso sobre MSI
        msi_warning = QLabel(
            "⚠️ Para gerar .MSI, o WiX Toolset deve estar instalado.\n"
            "Caso não esteja, será oferecido download automático."
        )
        msi_warning.setStyleSheet("color: #fb5607; font-style: italic;")
        msi_warning.setWordWrap(True)
        layout.addWidget(msi_warning)
        
        layout.addStretch()
        
    def _on_format_changed(self):
        """Quando formato é selecionado/deselecionado"""
        self._formats = []
        for key, cb in self.format_checks.items():
            if cb.isChecked():
                self._formats.append(key)
                
        self.formats_selected.emit(self._formats)
        self.validation_changed.emit(len(self._formats) > 0)
        
    def validate(self) -> bool:
        return len(self._formats) > 0
        
    def get_data(self) -> dict:
        return {'formats': self._formats}
        
    def initialize(self, config: dict):
        if 'formats' in config:
            for fmt in config['formats']:
                if fmt in self.format_checks:
                    self.format_checks[fmt].setChecked(True)
