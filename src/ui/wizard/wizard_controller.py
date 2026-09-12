"""
TOSKINSTALLER - Wizard Controller
Controla a navegação e validação das páginas do wizard
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtWidgets import QStackedWidget, QWidget
from typing import List, Optional, Any

from .page_project import ProjectSelectionPage
from .page_language import LanguageDetectionPage
from .page_tools import ToolInstallationPage
from .page_formats import PackageFormatsPage
from .page_ui_custom import UICustomizationPage
from .page_partners import PartnerAppsPage
from .page_shortcuts import ShortcutsPage
from .page_summary import SummaryPage

from src.core.logger import get_logger

logger = get_logger(__name__)


class WizardController(QObject):
    """Controlador do wizard de 8 etapas"""
    
    # Sinais
    current_step_changed = Signal(int, int)  # step_index, total_steps
    validation_changed = Signal(bool)
    progress_changed = Signal(float)  # 0.0 a 1.0
    
    def __init__(self, stacked_widget: QStackedWidget, parent=None):
        super().__init__(parent)
        
        self._stack = stacked_widget
        self._current_index = 0
        self._pages: List[QWidget] = []
        self._config = {}  # Configuração acumulada
        
        self._setup_pages()
        
    def _setup_pages(self):
        """Inicializa todas as páginas do wizard"""
        logger.info("Inicializando páginas do wizard")
        
        # Página 1: Seleção do Projeto
        page1 = ProjectSelectionPage()
        page1.project_selected.connect(self._on_project_selected)
        self._pages.append(page1)
        self._stack.addWidget(page1)
        
        # Página 2: Detecção de Linguagem
        page2 = LanguageDetectionPage()
        page2.language_confirmed.connect(self._on_language_confirmed)
        self._pages.append(page2)
        self._stack.addWidget(page2)
        
        # Página 3: Instalação de Ferramentas
        page3 = ToolInstallationPage()
        page3.tools_ready.connect(self._on_tools_ready)
        self._pages.append(page3)
        self._stack.addWidget(page3)
        
        # Página 4: Formatos do Pacote
        page4 = PackageFormatsPage()
        page4.formats_selected.connect(self._on_formats_selected)
        self._pages.append(page4)
        self._stack.addWidget(page4)
        
        # Página 5: Customização de UI
        page5 = UICustomizationPage()
        page5.ui_configured.connect(self._on_ui_configured)
        self._pages.append(page5)
        self._stack.addWidget(page5)
        
        # Página 6: Apps Parceiros
        page6 = PartnerAppsPage()
        page6.partners_configured.connect(self._on_partners_configured)
        self._pages.append(page6)
        self._stack.addWidget(page6)
        
        # Página 7: Atalhos e Configurações
        page7 = ShortcutsPage()
        page7.shortcuts_configured.connect(self._on_shortcuts_configured)
        self._pages.append(page7)
        self._stack.addWidget(page7)
        
        # Página 8: Resumo e Geração
        page8 = SummaryPage()
        page8.build_requested.connect(self._on_build_requested)
        self._pages.append(page8)
        self._stack.addWidget(page8)
        
        # Conectar validação de todas as páginas
        for page in self._pages:
            if hasattr(page, 'validation_changed'):
                page.validation_changed.connect(self._on_page_validation_changed)
                
        logger.info(f"{len(self._pages)} páginas inicializadas")
        
    def _on_project_selected(self, project_path: str):
        self._config['project_path'] = project_path
        
    def _on_language_confirmed(self, language: str, tool: str):
        self._config['language'] = language
        self._config['tool'] = tool
        
    def _on_tools_ready(self, tool_installed: bool):
        self._config['tool_installed'] = tool_installed
        
    def _on_formats_selected(self, formats: List[str]):
        self._config['formats'] = formats
        
    def _on_ui_configured(self, ui_config: dict):
        self._config.update(ui_config)
        
    def _on_partners_configured(self, partners: List[dict]):
        self._config['partners'] = partners
        
    def _on_shortcuts_configured(self, shortcuts_config: dict):
        self._config.update(shortcuts_config)
        
    def _on_build_requested(self):
        logger.info("Build solicitado pelo usuário")
        # TODO: Disparar processo de build
        
    @Slot(bool)
    def _on_page_validation_changed(self, is_valid: bool):
        """Atualiza estado de validação quando página muda"""
        self.validation_changed.emit(is_valid)
        
    def next_step(self):
        """Avança para próxima página"""
        if self._current_index < len(self._pages) - 1:
            # Validar página atual antes de avançar
            current_page = self._pages[self._current_index]
            if hasattr(current_page, 'validate') and not current_page.validate():
                logger.warning("Página atual não válida")
                return False
                
            self._current_index += 1
            self._stack.setCurrentIndex(self._current_index)
            self.current_step_changed.emit(self._current_index, len(self._pages))
            
            # Atualizar dados da próxima página
            self._update_next_page()
            
            logger.debug(f"Navegado para página {self._current_index}")
            return True
        return False
        
    def previous_step(self):
        """Volta para página anterior"""
        if self._current_index > 0:
            self._current_index -= 1
            self._stack.setCurrentIndex(self._current_index)
            self.current_step_changed.emit(self._current_index, len(self._pages))
            logger.debug(f"Retornado para página {self._current_index}")
            return True
        return False
        
    def _update_next_page(self):
        """Atualiza a próxima página com dados acumulados"""
        next_page = self._pages[self._current_index]
        
        # Passar configuração para página
        if hasattr(next_page, 'initialize'):
            next_page.initialize(self._config)
            
    def is_current_step_valid(self) -> bool:
        """Verifica se a página atual é válida"""
        current_page = self._pages[self._current_index]
        if hasattr(current_page, 'validate'):
            return current_page.validate()
        return True
        
    def is_last_step(self) -> bool:
        """Verifica se está na última página"""
        return self._current_index >= len(self._pages) - 1
        
    def get_current_step_index(self) -> int:
        """Retorna índice da página atual"""
        return self._current_index
        
    def get_total_steps(self) -> int:
        """Retorna total de páginas"""
        return len(self._pages)
        
    def get_config(self) -> dict:
        """Retorna configuração acumulada completa"""
        # Atualizar com dados da página atual antes de retornar
        current_page = self._pages[self._current_index]
        if hasattr(current_page, 'get_data'):
            current_data = current_page.get_data()
            self._config.update(current_data)
            
        return self._config.copy()
        
    def reset(self):
        """Reseta o wizard para o início"""
        self._current_index = 0
        self._config = {}
        self._stack.setCurrentIndex(0)
        self.current_step_changed.emit(0, len(self._pages))
        logger.info("Wizard resetado")
