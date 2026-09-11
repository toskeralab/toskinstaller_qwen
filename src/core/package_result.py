"""
TOSKINSTALLER - Package Result Model
Modelo para resultados de empacotamento

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from pathlib import Path


@dataclass
class PackageResult:
    """Resultado da geração de um pacote"""
    
    # Informações básicas
    success: bool
    package_path: Optional[Path] = None
    package_type: str = ""  # 'exe', 'msi', 'portable'
    
    # Metadados
    app_name: str = ""
    app_version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    
    # Detalhes técnicos
    file_size_bytes: int = 0
    architecture: str = "x64"
    
    # Logs e erros
    log_messages: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    
    # Caminhos relacionados
    temp_folder: Optional[Path] = None
    source_exe: Optional[Path] = None
    
    # Assinatura digital
    signed: bool = False
    certificate_subject: Optional[str] = None
    
    @property
    def file_size_mb(self) -> float:
        """Retorna tamanho em MB"""
        return self.file_size_bytes / (1024 * 1024)
    
    @property
    def is_valid(self) -> bool:
        """Verifica se o resultado é válido"""
        return self.success and self.package_path and self.package_path.exists()
    
    def add_log(self, message: str):
        """Adiciona mensagem de log"""
        self.log_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'success': self.success,
            'package_path': str(self.package_path) if self.package_path else None,
            'package_type': self.package_type,
            'app_name': self.app_name,
            'app_version': self.app_version,
            'created_at': self.created_at.isoformat(),
            'file_size_bytes': self.file_size_bytes,
            'file_size_mb': round(self.file_size_mb, 2),
            'architecture': self.architecture,
            'signed': self.signed,
            'certificate_subject': self.certificate_subject,
            'error_message': self.error_message,
            'log_count': len(self.log_messages)
        }
