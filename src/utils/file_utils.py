"""
TOSKINSTALLER - File Utilities
Utilitários para manipulação de arquivos

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

import shutil
import hashlib
from pathlib import Path
from typing import Optional, List


class FileUtils:
    """Utilitários para operações com arquivos"""
    
    @staticmethod
    def copy_file(src: Path, dst: Path, overwrite: bool = True) -> bool:
        """Copia arquivo com verificação"""
        try:
            if not src.exists():
                return False
            
            if dst.exists() and not overwrite:
                return False
            
            shutil.copy2(src, dst)
            return True
        except Exception:
            return False
    
    @staticmethod
    def copy_tree(src: Path, dst: Path, ignore_patterns: Optional[List[str]] = None) -> bool:
        """Copia árvore de diretórios"""
        try:
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*ignore_patterns) if ignore_patterns else None)
            return True
        except Exception:
            return False
    
    @staticmethod
    def remove_path(path: Path, force: bool = False) -> bool:
        """Remove arquivo ou diretório"""
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=not force)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_hash(file_path: Path, algorithm: str = "sha256") -> Optional[str]:
        """Calcula hash de arquivo"""
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """Retorna tamanho do arquivo em bytes"""
        return file_path.stat().st_size if file_path.exists() else 0
    
    @staticmethod
    def ensure_dir(path: Path) -> bool:
        """Garante que diretório existe"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def find_files(directory: Path, pattern: str = "*", recursive: bool = True) -> List[Path]:
        """Encontra arquivos por padrão"""
        if recursive:
            return list(directory.rglob(pattern))
        return list(directory.glob(pattern))
    
    @staticmethod
    def is_executable(path: Path) -> bool:
        """Verifica se arquivo é executável"""
        if not path.exists() or not path.is_file():
            return False
        
        # Windows verifica extensão
        executable_extensions = {'.exe', '.bat', '.cmd', '.com', '.ps1'}
        return path.suffix.lower() in executable_extensions
