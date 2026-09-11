"""
Página 2 - Detecção de Linguagem
Mostra linguagem detectada e permite confirmação/seleção manual
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QRadioButton, QButtonGroup, QFrame, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from ...core.logger import get_logger

logger = get_logger(__name__)


class LanguageDetectionPage(QWidget):
    """Página 2 - Confirmação de linguagem e ferramenta"""
    
    language_confirmed = Signal(str, str)  # linguagem, ferramenta
    validation_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._language = ""
        self._tool = ""
        self._project_metadata = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel("Linguagem Detectada")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        desc = QLabel(
            "Identificamos a linguagem do seu projeto. Confirme ou selecione manualmente."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Grupo de linguagens
        lang_group = QGroupBox("Linguagem do Projeto")
        lang_layout = QVBoxLayout(lang_group)
        
        self.lang_buttons = QButtonGroup(self)
        
        languages = [
            ("Python", "python", "PyInstaller / Nuitka"),
            ("Node.js", "nodejs", "pkg / electron-builder"),
            ("C# (.NET)", "csharp", "dotnet publish"),
        ]
        
        for i, (label, value, tools) in enumerate(languages):
            rb = QRadioButton(f"{label} - {tools}")
            rb.setProperty("language", value)
            self.lang_buttons.addButton(rb, i)
            lang_layout.addWidget(rb)
            
        self.lang_buttons.buttonClicked.connect(self._on_language_selected)
        layout.addWidget(lang_group)
        
        # Ferramenta recomendada
        tool_group = QGroupBox("Ferramenta de Compilação")
        tool_layout = QVBoxLayout(tool_group)
        
        self.tool_label = QLabel("Selecione uma linguagem primeiro")
        self.tool_label.setWordWrap(True)
        tool_layout.addWidget(self.tool_label)
        
        layout.addWidget(tool_group)
        layout.addStretch()
        
    def _on_language_selected(self, button):
        lang = button.property("language")
        self._language = lang
        
        tools_map = {
            "python": "PyInstaller (recomendado)",
            "nodejs": "pkg",
            "csharp": "dotnet publish"
        }
        
        self.tool_label.setText(f"Ferramenta: {tools_map.get(lang, 'N/A')}")
        self._tool = tools_map.get(lang, "")
        
        self.language_confirmed.emit(lang, self._tool)
        self.validation_changed.emit(True)
        
    def validate(self) -> bool:
        return bool(self._language)
        
    def get_data(self) -> dict:
        return {'language': self._language, 'tool': self._tool}
        
    def initialize(self, config: dict):
        if 'project_metadata' in config and config['project_metadata']:
            meta = config['project_metadata']
            lang = meta.get('language', '').lower()
            
            if 'python' in lang:
                self.lang_buttons.buttons()[0].setChecked(True)
                self._on_language_selected(self.lang_buttons.buttons()[0])
            elif 'node' in lang:
                self.lang_buttons.buttons()[1].setChecked(True)
                self._on_language_selected(self.lang_buttons.buttons()[1])
            elif 'c#' in lang or 'csharp' in lang or 'dotnet' in lang:
                self.lang_buttons.buttons()[2].setChecked(True)
                self._on_language_selected(self.lang_buttons.buttons()[2])
