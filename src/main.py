#!/usr/bin/env python3
"""
TOSKINSTALLER - Main Entry Point
Desenvolvido por ToskeraLAB ART/TECH House
"""

import sys
import os

# Obter o diretório absoluto onde main.py reside (dentro de src/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subir um nível para obter a RAIZ do projeto
project_root = os.path.dirname(current_dir)
# Adicionar a raiz ao sys.path se ainda não existir
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QFont

from src.ui.main_window import MainWindow
from src.core.logger import get_logger

logger = get_logger(__name__)


def load_stylesheet(theme_name: str = 'toskera') -> str:
    """Carrega o stylesheet do tema selecionado"""
    themes_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'src', 'ui', 'resources', 'themes'
    )
    
    theme_files = {
        'light': 'light.qss',
        'dark': 'dark.qss',
        'toskera': 'toskera.qss'
    }
    
    qss_file = theme_files.get(theme_name, 'toskera.qss')
    qss_path = os.path.join(themes_path, qss_file)
    
    if os.path.exists(qss_path):
        with open(qss_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def main():
    """Função principal de entrada"""
    
    # High DPI é habilitado por padrão nas versões recentes do Qt
    # As configurações AA_EnableHighDpiScaling e AA_UseHighDpiPixmaps foram removidas
    
    app = QApplication(sys.argv)
    
    # Configurações globais
    app.setApplicationName("TOSKINSTALLER")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ToskeraLAB")
    app.setOrganizationDomain("toskeralab.com")
    
    # Fonte padrão
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Carregar tema padrão
    stylesheet = load_stylesheet('toskera')
    app.setStyleSheet(stylesheet)
    
    logger.info("=" * 60)
    logger.info("TOSKINSTALLER v1.0.0 - ToskeraLAB ART/TECH House")
    logger.info("=" * 60)
    
    # Criar e mostrar janela principal
    window = MainWindow()
    window.show()
    
    logger.info("Aplicação iniciada com sucesso")
    
    # Executar aplicação
    exit_code = app.exec()
    
    logger.info(f"Aplicação finalizada com código {exit_code}")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
