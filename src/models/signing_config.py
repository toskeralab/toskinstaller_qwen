"""
TOSKINSTALLER - Signing Configuration Model
Configuração de assinatura digital

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

from dataclasses import dataclass


@dataclass
class SigningConfig:
    """Configuração para assinatura digital de código"""
    enabled: bool = False
    certificate_path: str = ""
    password: str = ""
    timestamp_url: str = "http://timestamp.digicert.com"
    subject_name: str = ""
    algorithm: str = "SHA256"
    
    @property
    def is_valid(self) -> bool:
        """Verifica se configuração é válida"""
        return self.enabled and bool(self.certificate_path)
    
    def to_dict(self) -> dict:
        return {
            'enabled': self.enabled,
            'certificate_path': self.certificate_path,
            'subject_name': self.subject_name,
            'algorithm': self.algorithm,
            'timestamp_url': self.timestamp_url
        }
