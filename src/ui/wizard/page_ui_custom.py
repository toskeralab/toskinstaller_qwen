"""
Página 5 - Customização de UI
Logo, temas, cores e animações do instalador
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, 
    QGroupBox, QHBoxLayout, QFrame
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QColorDialog

from src.core.logger import get_logger

logger = get_logger(__name__)


class UICustomizationPage(QWidget):
    """Página 5 - Customização da interface do instalador"""
    
    ui_configured = Signal(dict)
    validation_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui_config = {
            'theme': 'toskera',
            'animation': 'toskera',
            'primary_color': '#ff006e',
            'secondary_color': '#8338ec'
        }
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel("Customizar Interface")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        desc = QLabel(
            "Personalize a aparência do instalador com temas, cores e animações."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Tema
        theme_group = QGroupBox("Tema de Cores")
        theme_layout = QHBoxLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Claro", "Escuro", "ToskeraLAB"])
        self.theme_combo.setCurrentIndex(2)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(theme_group)
        
        # Animação
        anim_group = QGroupBox("Animação de Progresso")
        anim_layout = QHBoxLayout(anim_group)
        
        self.anim_combo = QComboBox()
        self.anim_combo.addItems([
            "Círculo Giratório",
            "Barra Gradiente", 
            "Pontos Pulsantes",
            "Pulso Radial",
            "ToskeraLAB Edition"
        ])
        self.anim_combo.setCurrentIndex(4)
        self.anim_combo.currentIndexChanged.connect(self._on_anim_changed)
        anim_layout.addWidget(self.anim_combo)
        
        layout.addWidget(anim_group)
        
        # Cores customizadas
        color_group = QGroupBox("Cores Personalizadas")
        color_layout = QVBoxLayout(color_group)
        
        # Cor primária
        primary_layout = QHBoxLayout()
        primary_label = QLabel("Cor Primária:")
        self.primary_color_btn = QPushButton()
        self.primary_color_btn.setStyleSheet(f"background-color: {self._ui_config['primary_color']};")
        self.primary_color_btn.clicked.connect(lambda: self._pick_color('primary'))
        primary_layout.addWidget(primary_label)
        primary_layout.addWidget(self.primary_color_btn)
        color_layout.addLayout(primary_layout)
        
        # Cor secundária
        secondary_layout = QHBoxLayout()
        secondary_label = QLabel("Cor Secundária:")
        self.secondary_color_btn = QPushButton()
        self.secondary_color_btn.setStyleSheet(f"background-color: {self._ui_config['secondary_color']};")
        self.secondary_color_btn.clicked.connect(lambda: self._pick_color('secondary'))
        secondary_layout.addWidget(secondary_label)
        secondary_layout.addWidget(self.secondary_color_btn)
        color_layout.addLayout(secondary_layout)
        
        layout.addWidget(color_group)
        
        # Preview placeholder
        preview_frame = QFrame()
        preview_frame.setObjectName("previewFrame")
        preview_layout = QVBoxLayout(preview_frame)
        preview_label = QLabel("Preview da animação será exibido aqui")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(preview_label)
        layout.addWidget(preview_frame)
        
        layout.addStretch()
        
    def _on_theme_changed(self, index):
        themes = ['light', 'dark', 'toskera']
        self._ui_config['theme'] = themes[index] if index < len(themes) else 'toskera'
        self._emit_config()
        
    def _on_anim_changed(self, index):
        animations = ['circle', 'bar', 'dots', 'pulse', 'toskera']
        self._ui_config['animation'] = animations[index] if index < len(animations) else 'toskera'
        self._emit_config()
        
    def _pick_color(self, color_type: str):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self._ui_config[f'{color_type}_color'] = hex_color
            
            btn = self.primary_color_btn if color_type == 'primary' else self.secondary_color_btn
            btn.setStyleSheet(f"background-color: {hex_color};")
            
            self._emit_config()
            
    def _emit_config(self):
        self.ui_configured.emit(self._ui_config)
        self.validation_changed.emit(True)
        
    def validate(self) -> bool:
        return True  # Sempre válido, tem defaults
        
    def get_data(self) -> dict:
        return {'ui_config': self._ui_config}
        
    def initialize(self, config: dict):
        if 'ui_config' in config:
            self._ui_config.update(config['ui_config'])
