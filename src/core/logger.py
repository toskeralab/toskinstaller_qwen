"""
TOSKINSTALLER - Sistema de Logging

Logging estruturado com suporte a cores e múltiplos níveis.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para console."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        reset = Style.RESET_ALL if COLORAMA_AVAILABLE else ''
        
        if COLORAMA_AVAILABLE:
            record.levelname = f"{log_color}{record.levelname}{reset}"
        
        return super().format(record)


def setup_logger(
    name: str = "toskinstaller",
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console_output: bool = True
) -> logging.Logger:
    """
    Configura e retorna um logger configurado.
    
    Args:
        name: Nome do logger
        log_file: Caminho para arquivo de log (opcional)
        level: Nível de logging
        console_output: Se deve outputar para console
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formatter padrão
    format_str = "%(asctime)s | %(levelname)-8s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Handler de console
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if COLORAMA_AVAILABLE:
            console_formatter = ColoredFormatter(format_str, datefmt=date_format)
        else:
            console_formatter = logging.Formatter(format_str, datefmt=date_format)
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Handler de arquivo
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        
        file_formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt=date_format
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Logger global padrão
logger = setup_logger()


def get_logger(name: str = "toskinstaller") -> logging.Logger:
    """Obtém ou cria um logger com o nome especificado."""
    return logging.getLogger(name)
