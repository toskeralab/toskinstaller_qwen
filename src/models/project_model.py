"""
TOSKINSTALLER - Project Model
Modelo para informações do projeto

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class ProjectInfo:
    """Informações sobre o projeto a ser empacotado"""
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    language: str = ""
    project_path: Optional[Path] = None
    
    # Ferramentas recomendadas
    recommended_tools: List[str] = field(default_factory=list)
    
    # Arquivos principais
    main_file: Optional[Path] = None
    entry_point: str = ""
    
    # Dependências
    dependencies: List[str] = field(default_factory=list)
    
    # Metadata adicional
    metadata: dict = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Verifica se projeto é válido"""
        return bool(self.name) and bool(self.project_path)
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'language': self.language,
            'project_path': str(self.project_path) if self.project_path else None,
            'main_file': str(self.main_file) if self.main_file else None,
            'entry_point': self.entry_point,
            'dependencies': self.dependencies,
            'recommended_tools': self.recommended_tools,
            'metadata': self.metadata
        }
