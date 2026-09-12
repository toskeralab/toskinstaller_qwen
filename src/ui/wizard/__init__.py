"""
TOSKINSTALLER - Páginas do Wizard
Coleção de todas as páginas da interface wizard
"""

from src.ui.wizard.page_project import ProjectSelectionPage
from src.ui.wizard.page_language import LanguageDetectionPage
from src.ui.wizard.page_tools import ToolInstallationPage
from src.ui.wizard.page_formats import PackageFormatsPage
from src.ui.wizard.page_ui_custom import UICustomizationPage
from src.ui.wizard.page_partners import PartnerAppsPage
from src.ui.wizard.page_shortcuts import ShortcutsPage
from src.ui.wizard.page_summary import SummaryPage

__all__ = [
    'ProjectSelectionPage',
    'LanguageDetectionPage',
    'ToolInstallationPage',
    'PackageFormatsPage',
    'UICustomizationPage',
    'PartnerAppsPage',
    'ShortcutsPage',
    'SummaryPage'
]