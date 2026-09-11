"""
Página 6 - Apps Parceiros
Configuração de aplicativos adicionais para instalação
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, 
    QGroupBox, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from ...core.logger import get_logger

logger = get_logger(__name__)


class PartnerAppsPage(QWidget):
    """Página 6 - Configuração de apps parceiros"""
    
    partners_configured = Signal(list)
    validation_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._partners = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel("Apps Parceiros")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        desc = QLabel(
            "Adicione aplicativos que serão instalados junto com seu app.\n"
            "Exemplos: VC++ Redistributable, .NET Runtime, DirectX."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Lista de apps
        list_group = QGroupBox("Aplicativos Adicionais")
        list_layout = QVBoxLayout(list_group)
        
        self.partners_list = QListWidget()
        list_layout.addWidget(self.partners_list)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("+ Adicionar App")
        add_btn.clicked.connect(self._on_add_partner)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("- Remover")
        remove_btn.clicked.connect(self._on_remove_partner)
        btn_layout.addWidget(remove_btn)
        
        btn_layout.addStretch()
        
        list_layout.addLayout(btn_layout)
        layout.addWidget(list_group)
        
        layout.addStretch()
        
    def _on_add_partner(self):
        """Adiciona app parceiro"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Adicionar App")
        msg.setText(
            "Para adicionar um app parceiro:\n\n"
            "1. Selecione o executável/MSI do app\n"
            "2. Defina se instala antes ou depois do app principal\n"
            "3. Opcional: argumentos de linha de comando"
        )
        msg.exec()
        
        # Placeholder - adiciona item demo
        self.partners_list.addItem("VC++ Redistributable (exemplo)")
        self._update_partners()
        
    def _on_remove_partner(self):
        """Remove app selecionado"""
        current = self.partners_list.currentRow()
        if current >= 0:
            self.partners_list.takeItem(current)
            self._update_partners()
            
    def _update_partners(self):
        """Atualiza lista interna e emite sinal"""
        self._partners = []
        for i in range(self.partners_list.count()):
            item = self.partners_list.item(i)
            self._partners.append({'name': item.text()})
            
        self.partners_configured.emit(self._partners)
        self.validation_changed.emit(True)
        
    def validate(self) -> bool:
        return True  # Apps parceiros são opcionais
        
    def get_data(self) -> dict:
        return {'partners': self._partners}
        
    def initialize(self, config: dict):
        if 'partners' in config:
            for partner in config['partners']:
                self.partners_list.addItem(partner.get('name', 'App'))
            self._update_partners()
