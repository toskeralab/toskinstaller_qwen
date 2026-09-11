"""
TOSKINSTALLER - Partner App Model
Modelo para aplicativos parceiros

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PartnerApp:
    """Aplicativo parceiro para instalação opcional"""
    name: str
    path: str
    version: str = "1.0.0"
    publisher: str = ""
    install_order: int = 0
    install_after_main: bool = True
    silent_install: bool = True
    required: bool = False
    description: str = ""
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'path': self.path,
            'version': self.version,
            'publisher': self.publisher,
            'install_order': self.install_order,
            'install_after_main': self.install_after_main,
            'silent_install': self.silent_install,
            'required': self.required,
            'description': self.description
        }
