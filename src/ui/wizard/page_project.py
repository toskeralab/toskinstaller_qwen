"""
Página 1 - Seleção do Projeto
Permite ao usuário selecionar a pasta do projeto a ser empacotado
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFileDialog, QFrame
)
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont

from src.core.logger import get_logger
from src.core.detector import ProjectDetector

logger = get_logger(__name__)


class ProjectSelectionPage(QWidget):
    """Primeira página do wizard - Seleção do projeto"""
    
    project_selected = Signal(str)  # caminho do projeto
    validation_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_path = ""
        self._detector = ProjectDetector()
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Selecionar Projeto")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        # Descrição
        desc = QLabel(
            "Selecione a pasta contendo o projeto que será convertido em executável.\n"
            "Projetos Python, Node.js e C# são suportados."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Espaço
        layout.addSpacing(20)
        
        # Campo de caminho
        path_layout = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Caminho da pasta do projeto...")
        self.path_edit.textChanged.connect(self._on_path_changed)
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Procurar...")
        browse_btn.clicked.connect(self._on_browse_clicked)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # Frame de informações do projeto detectado
        self.info_frame = QFrame()
        self.info_frame.setObjectName("infoFrame")
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        self.info_label = QLabel("Nenhum projeto selecionado")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        self.info_frame.setVisible(False)
        layout.addWidget(self.info_frame)
        
        layout.addStretch()
        
    @Slot()
    def _on_browse_clicked(self):
        """Abre dialog para selecionar pasta"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta do Projeto",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            self.path_edit.setText(folder)
            
    @Slot(str)
    def _on_path_changed(self, path: str):
        """Quando o caminho muda, detectar projeto"""
        self._project_path = path
        
        if path and self._detector.detect_project(path):
            # Projeto detectado com sucesso
            metadata = self._detector.get_metadata()
            self.info_label.setText(
                f"✅ Projeto detectado:\n"
                f"• Linguagem: {metadata.get('language', 'Desconhecida')}\n"
                f"• Nome: {metadata.get('name', 'N/A')}\n"
                f"• Versão: {metadata.get('version', 'N/A')}\n"
                f"• Confiança: {metadata.get('confidence', 0):.0%}"
            )
            self.info_frame.setVisible(True)
            self.project_selected.emit(path)
            self.validation_changed.emit(True)
        else:
            self.info_frame.setVisible(False)
            self.validation_changed.emit(False)
            
    def validate(self) -> bool:
        """Valida se um projeto foi selecionado"""
        return bool(self._project_path and self._detector.is_valid())
        
    def get_data(self) -> dict:
        """Retorna dados desta página"""
        return {
            'project_path': self._project_path,
            'project_metadata': self._detector.get_metadata() if self._detector.is_valid() else None
        }
        
    def initialize(self, config: dict):
        """Inicializa página com configuração"""
        if 'project_path' in config:
            self.path_edit.setText(config['project_path'])
