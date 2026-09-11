"""
Página 8 - Resumo e Geração
Mostra resumo da configuração e inicia build
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, 
    QFrame, QMessageBox
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from ...core.logger import get_logger

logger = get_logger(__name__)


class SummaryPage(QWidget):
    """Página 8 - Resumo final e geração do pacote"""
    
    build_requested = Signal()
    validation_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel("Resumo e Geração")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        desc = QLabel(
            "Revise as configurações antes de gerar o pacote final."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Resumo
        summary_group = QFrame()
        summary_group.setObjectName("summaryFrame")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(300)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        # Botão gerar
        generate_btn = QPushButton("🚀 Gerar Pacote")
        generate_btn.setObjectName("nextButton")
        generate_btn.setMinimumHeight(50)
        generate_btn.clicked.connect(self._on_generate)
        layout.addWidget(generate_btn)
        
        layout.addStretch()
        
    def _on_generate(self):
        """Inicia processo de geração"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Gerar Pacote")
        msg.setText("Deseja iniciar a geração do pacote?")
        msg.setInformativeText("Isso pode levar alguns minutos.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            self.build_requested.emit()
            
    def validate(self) -> bool:
        return True
        
    def get_data(self) -> dict:
        return {}
        
    def initialize(self, config: dict):
        """Preenche resumo com configuração"""
        summary = "=== RESUMO DA CONFIGURAÇÃO ===\n\n"
        
        summary += f"📁 Projeto: {config.get('project_path', 'N/A')}\n"
        summary += f"🔧 Linguagem: {config.get('language', 'N/A')}\n"
        summary += f"⚙️ Ferramenta: {config.get('tool', 'N/A')}\n\n"
        
        summary += f"📦 Formatos: {', '.join(config.get('formats', []))}\n\n"
        
        ui_config = config.get('ui_config', {})
        summary += f"🎨 Tema: {ui_config.get('theme', 'default')}\n"
        summary += f"✨ Animação: {ui_config.get('animation', 'default')}\n\n"
        
        summary += f"🔗 Atalho Desktop: {'Sim' if config.get('create_desktop', False) else 'Não'}\n"
        summary += f"📋 Menu Iniciar: {'Sim' if config.get('create_start_menu', False) else 'Não'}\n"
        summary += f"🏗️ Arquitetura: {config.get('architecture', 'x64')}\n"
        
        partners = config.get('partners', [])
        if partners:
            summary += f"\n🤝 Apps Parceiros: {len(partners)}\n"
            
        self.summary_text.setText(summary)
        self.validation_changed.emit(True)
