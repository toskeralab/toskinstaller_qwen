"""
TOSKINSTALLER - Páginas do Wizard
Coleção de todas as páginas da interface wizard
"""

from .page_project import ProjectSelectionPage
from .page_language import LanguageDetectionPage
from .page_tools import ToolInstallationPage
from .page_formats import PackageFormatsPage
from .page_ui_custom import UICustomizationPage
from .page_partners import PartnerAppsPage
from .page_shortcuts import ShortcutsPage
from .page_summary import SummaryPage

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