"""
TOSKINSTALLER - Detector de Linguagem de Projetos

Detecta automaticamente a linguagem de um projeto analisando arquivos característicos.
Suporta detecção híbrida: automática + confirmação manual.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .logger import get_logger

logger = get_logger(__name__)


class Language(Enum):
    """Linguagens suportadas."""
    PYTHON = "python"
    NODEJS = "nodejs"
    CSHARP = "csharp"
    UNKNOWN = "unknown"


class BuildTool(Enum):
    """Ferramentas de build suportadas."""
    # Python
    PYINSTALLER = "pyinstaller"
    Nuitka = "nuitka"
    CX_FREEZE = "cx_freeze"
    
    # Node.js
    PKG = "pkg"
    ELECTRON_BUILDER = "electron_builder"
    
    # C#
    DOTNET_PUBLISH = "dotnet_publish"
    MSBUILD = "msbuild"


@dataclass
class ProjectInfo:
    """Informações sobre o projeto detectado."""
    path: Path
    language: Language
    confidence: float  # 0.0 a 1.0
    detected_files: List[str]
    recommended_tools: List[BuildTool]
    main_file: Optional[str] = None
    name: str = ""
    version: str = "1.0.0"
    
    def to_dict(self) -> dict:
        return {
            'path': str(self.path),
            'language': self.language.value,
            'confidence': self.confidence,
            'detected_files': self.detected_files,
            'recommended_tools': [t.value for t in self.recommended_tools],
            'main_file': self.main_file,
            'name': self.name,
            'version': self.version,
        }


class ProjectDetector:
    """
    Detector de linguagem de projetos.
    
    Analisa arquivos característicos para identificar a linguagem
    e sugerir ferramentas de compilação apropriadas.
    """
    
    # Arquivos característicos por linguagem
    LANGUAGE_SIGNATURES: Dict[Language, List[str]] = {
        Language.PYTHON: [
            'requirements.txt',
            'setup.py',
            'pyproject.toml',
            '__main__.py',
            '.py',
        ],
        Language.NODEJS: [
            'package.json',
            'package-lock.json',
            'yarn.lock',
            '.js',
            '.ts',
        ],
        Language.CSHARP: [
            '.csproj',
            '.sln',
            '.cs',
            'appsettings.json',
        ],
    }
    
    # Ferramentas recomendadas por linguagem
    TOOL_RECOMMENDATIONS: Dict[Language, List[Tuple[BuildTool, float]]] = {
        Language.PYTHON: [
            (BuildTool.Nuitka, 0.95),      # Performance melhor
            (BuildTool.PYINSTALLER, 0.90),  # Compatibilidade máxima
            (BuildTool.CX_FREEZE, 0.75),
        ],
        Language.NODEJS: [
            (BuildTool.PKG, 0.90),
            (BuildTool.ELECTRON_BUILDER, 0.80),
        ],
        Language.CSHARP: [
            (BuildTool.DOTNET_PUBLISH, 0.95),
            (BuildTool.MSBUILD, 0.85),
        ],
    }
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def detect(self, project_path: str, auto_confirm: bool = True) -> ProjectInfo:
        """
        Detecta a linguagem de um projeto.
        
        Args:
            project_path: Caminho para a pasta do projeto
            auto_confirm: Se True, retorna detecção automática; se False, aguarda confirmação
        
        Returns:
            ProjectInfo com dados do projeto detectado
        """
        path = Path(project_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Projeto não encontrado: {project_path}")
        
        if not path.is_dir():
            raise ValueError(f"Caminho deve ser uma pasta: {project_path}")
        
        self.logger.info(f"Analisando projeto em: {path}")
        
        # Analisar arquivos
        detected_files = self._scan_files(path)
        
        # Calcular scores por linguagem
        scores = self._calculate_scores(detected_files)
        
        # Determinar linguagem mais provável
        if not scores:
            self.logger.warning("Nenhuma linguagem reconhecida detectada")
            return self._create_unknown_project(path)
        
        best_language = max(scores.items(), key=lambda x: x[1])
        language, confidence = best_language
        
        self.logger.info(f"Linguagem detectada: {language.value} (confiança: {confidence:.2f})")
        
        # Obter ferramentas recomendadas
        recommended_tools = self._get_recommended_tools(language)
        
        # Tentar encontrar arquivo principal
        main_file = self._find_main_file(path, language)
        
        # Tentar extrair nome e versão
        name, version = self._extract_metadata(path, language)
        
        return ProjectInfo(
            path=path,
            language=language,
            confidence=confidence,
            detected_files=detected_files,
            recommended_tools=recommended_tools,
            main_file=main_file,
            name=name or path.name,
            version=version,
        )
    
    def _scan_files(self, path: Path) -> List[str]:
        """Varre arquivos do projeto."""
        detected = []
        
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    # Caminho relativo
                    rel_path = str(item.relative_to(path))
                    
                    # Ignorar diretórios comuns
                    if any(skip in rel_path for skip in ['__pycache__', 'node_modules', '.git', 'venv', 'env']):
                        continue
                    
                    detected.append(rel_path)
                    
                    # Limitar a 500 arquivos para performance
                    if len(detected) >= 500:
                        break
        except Exception as e:
            self.logger.error(f"Erro ao varrer arquivos: {e}")
        
        return detected
    
    def _calculate_scores(self, files: List[str]) -> Dict[Language, float]:
        """Calcula score de confiança para cada linguagem."""
        scores: Dict[Language, float] = {}
        
        for language, signatures in self.LANGUAGE_SIGNATURES.items():
            score = 0.0
            
            for sig in signatures:
                if sig.startswith('.'):
                    # Extensão de arquivo
                    matching = [f for f in files if f.endswith(sig)]
                    score += len(matching) * 0.1
                else:
                    # Arquivo exato
                    if sig in files:
                        score += 0.3
            
            if score > 0:
                # Normalizar score para 0-1
                scores[language] = min(1.0, score)
        
        return scores
    
    def _get_recommended_tools(self, language: Language) -> List[BuildTool]:
        """Obtém lista de ferramentas recomendadas para linguagem."""
        recommendations = self.TOOL_RECOMMENDATIONS.get(language, [])
        return [tool for tool, _ in sorted(recommendations, key=lambda x: -x[1])]
    
    def _find_main_file(self, path: Path, language: Language) -> Optional[str]:
        """Tenta encontrar o arquivo principal do projeto."""
        main_candidates = {
            Language.PYTHON: ['main.py', 'app.py', '__main__.py', 'index.py'],
            Language.NODEJS: ['index.js', 'app.js', 'main.js', 'server.js'],
            Language.CSHARP: ['Program.cs', 'Startup.cs', 'Main.cs'],
        }
        
        candidates = main_candidates.get(language, [])
        
        for candidate in candidates:
            if (path / candidate).exists():
                return candidate
        
        # Fallback: buscar primeiro arquivo .py/.js/.cs na raiz
        for item in path.iterdir():
            if item.is_file():
                ext = item.suffix.lower()
                if language == Language.PYTHON and ext == '.py':
                    return item.name
                elif language == Language.NODEJS and ext in ['.js', '.ts']:
                    return item.name
                elif language == Language.CSHARP and ext == '.cs':
                    return item.name
        
        return None
    
    def _extract_metadata(self, path: Path, language: Language) -> Tuple[Optional[str], Optional[str]]:
        """Extrai nome e versão do projeto."""
        name = None
        version = None
        
        try:
            if language == Language.PYTHON:
                # requirements.txt
                req_file = path / 'requirements.txt'
                if req_file.exists():
                    with open(req_file, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line and not first_line.startswith('#'):
                            name = first_line.split('==')[0].split('[')[0]
                
                # setup.py
                setup_file = path / 'setup.py'
                if setup_file.exists():
                    content = setup_file.read_text(encoding='utf-8')
                    if 'name=' in content:
                        import re
                        match = re.search(r"name=['\"]([^'\"]+)['\"]", content)
                        if match:
                            name = match.group(1)
                    if 'version=' in content:
                        import re
                        match = re.search(r"version=['\"]([^'\"]+)['\"]", content)
                        if match:
                            version = match.group(1)
                
                # pyproject.toml
                pyproject = path / 'pyproject.toml'
                if pyproject.exists():
                    content = pyproject.read_text(encoding='utf-8')
                    import re
                    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                    if name_match:
                        name = name_match.group(1)
                    version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    if version_match:
                        version = version_match.group(1)
            
            elif language == Language.NODEJS:
                pkg_file = path / 'package.json'
                if pkg_file.exists():
                    import json
                    pkg = json.loads(pkg_file.read_text(encoding='utf-8'))
                    name = pkg.get('name')
                    version = pkg.get('version')
            
            elif language == Language.CSHARP:
                # Buscar .csproj
                csproj_files = list(path.glob('*.csproj'))
                if csproj_files:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(csproj_files[0])
                    root = tree.getroot()
                    
                    # Namespace handling
                    ns = {'msb': 'http://schemas.microsoft.com/developer/msbuild/2003'}
                    
                    name_elem = root.find('.//AssemblyName', ns)
                    if name_elem is not None and name_elem.text:
                        name = name_elem.text
                    
                    version_elem = root.find('.//Version', ns)
                    if version_elem is not None and version_elem.text:
                        version = version_elem.text
        except Exception as e:
            self.logger.debug(f"Erro ao extrair metadata: {e}")
        
        return name, version
    
    def _create_unknown_project(self, path: Path) -> ProjectInfo:
        """Cria ProjectInfo para projeto não reconhecido."""
        return ProjectInfo(
            path=path,
            language=Language.UNKNOWN,
            confidence=0.0,
            detected_files=[],
            recommended_tools=[],
            name=path.name,
        )
    
    def validate_detection(self, project_info: ProjectInfo) -> bool:
        """Valida se a detecção é confiável o suficiente."""
        return project_info.confidence >= 0.5 and project_info.language != Language.UNKNOWN
    
    def get_alternative_languages(self, files: List[str]) -> List[Tuple[Language, float]]:
        """Retorna linguagens alternativas com scores."""
        scores = self._calculate_scores(files)
        return sorted(scores.items(), key=lambda x: -x[1])
