"""
Página 3 - Instalação de Ferramentas
Verifica e orienta instalação de ferramentas externas
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, 
    QProgressBar, QCheckBox, QMessageBox
)
from PySide6.QtCore import Signal, Qt, QThread
from PySide6.QtGui import QFont

from src.core.logger import get_logger

logger = get_logger(__name__)


class ToolInstallationPage(QWidget):
    """Página 3 - Verificação e instalação de ferramentas"""
    
    tools_ready = Signal(bool)
    validation_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tool_installed = False
        self._tool_name = ""
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel("Ferramentas Necessárias")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        desc = QLabel(
            "Verificando se as ferramentas necessárias estão instaladas...\n"
            "Caso não estejam, orientaremos a instalação."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Status da ferramenta
        self.status_frame = QFrame()
        status_layout = QVBoxLayout(self.status_frame)
        
        self.status_label = QLabel("Aguardando detecção da linguagem...")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        status_layout.addWidget(self.progress)
        
        layout.addWidget(self.status_frame)
        
        # Botões de ação
        action_layout = QVBoxLayout()
        
        self.install_btn = QPushButton("Instalar Ferramenta")
        self.install_btn.setObjectName("nextButton")
        self.install_btn.clicked.connect(self._on_install_clicked)
        self.install_btn.setEnabled(False)
        action_layout.addWidget(self.install_btn)
        
        self.skip_btn = QPushButton("Pular (ferramenta já instalada)")
        self.skip_btn.clicked.connect(self._on_skip_clicked)
        action_layout.addWidget(self.skip_btn)
        
        layout.addLayout(action_layout)
        layout.addStretch()
        
    def _on_install_clicked(self):
        """Inicia instalação da ferramenta"""
        logger.info(f"Iniciando instalação de {self._tool_name}")
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Instalação")
        msg.setText(f"Para instalar {self._tool_name}:\n\n"
                   f"1. Abra o Terminal/CMD como Administrador\n"
                   f"2. Execute: pip install {self._tool_name.lower()}\n"
                   f"3. Reinicie o TOSKINSTALLER\n\n"
                   f"Ou visite: https://pypi.org/project/{self._tool_name.lower()}/")
        msg.exec()
        
    def _on_skip_clicked(self):
        """Pula verificação (usuário afirma que já está instalado)"""
        self._tool_installed = True
        self.tools_ready.emit(True)
        self.validation_changed.emit(True)
        
    def validate(self) -> bool:
        return self._tool_installed
        
    def get_data(self) -> dict:
        return {'tool_installed': self._tool_installed}
        
    def initialize(self, config: dict):
        tool = config.get('tool', '')
        language = config.get('language', '')
        
        if language == 'python':
            self._tool_name = 'PyInstaller'
            self.status_label.setText(
                f"Ferramenta necessária: {self._tool_name}\n\n"
                f"Verificando instalação..."
            )
            self.install_btn.setEnabled(True)
        elif language == 'nodejs':
            self._tool_name = 'pkg'
            self.status_label.setText(
                f"Ferramenta necessária: {self._tool_name}\n\n"
                f"Verificando instalação..."
            )
            self.install_btn.setEnabled(True)
        else:
            self.status_label.setText("Linguagem não suportada ainda")
            self.install_btn.setEnabled(False)
