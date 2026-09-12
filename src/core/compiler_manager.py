"""
TOSKINSTALLER - Gerenciador de Compilação

Orquestra múltiplas ferramentas de compilação para converter projetos em executáveis.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Type
from abc import ABC, abstractmethod

from .logger import get_logger
from .detector import ProjectInfo, Language, BuildTool

logger = get_logger(__name__)


class BaseCompiler(ABC):
    """Classe base para ferramentas de compilação."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def is_installed(self) -> bool:
        """Verifica se a ferramenta está instalada."""
        pass
    
    @abstractmethod
    def get_install_url(self) -> str:
        """Retorna URL de download/installação."""
        pass
    
    @abstractmethod
    def compile(self, project_info: ProjectInfo, output_dir: str) -> bool:
        """Executa compilação."""
        pass
    
    def install_instructions(self) -> str:
        """Retorna instruções de instalação."""
        return f"Instale {self.__class__.__name__} via: {self.get_install_url()}"


class PyInstallerTool(BaseCompiler):
    """Wrapper para PyInstaller."""
    
    def is_installed(self) -> bool:
        try:
            import PyInstaller
            return True
        except ImportError:
            return False
    
    def get_install_url(self) -> str:
        return "https://pypi.org/project/pyinstaller/"
    
    def compile(self, project_info: ProjectInfo, output_dir: str) -> bool:
        """Compila projeto Python com PyInstaller."""
        if not project_info.main_file:
            self.logger.error("Arquivo principal não encontrado")
            return False
        
        main_path = project_info.path / project_info.main_file
        
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--distpath", output_dir,
            "--workpath", str(Path(output_dir) / "build"),
            "--specpath", str(Path(output_dir) / "spec"),
            str(main_path),
        ]
        
        # Adicionar icon se existir
        icon_path = project_info.path / "icon.ico"
        if icon_path.exists():
            cmd.insert(3, f"--icon={icon_path}")
        
        self.logger.info(f"Executando PyInstaller: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("PyInstaller concluído com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"PyInstaller falhou: {e.stderr}")
            return False


class NuitkaTool(BaseCompiler):
    """Wrapper para Nuitka."""
    
    def is_installed(self) -> bool:
        try:
            import nuitka
            return True
        except ImportError:
            return False
    
    def get_install_url(self) -> str:
        return "https://nuitka.net/"
    
    def compile(self, project_info: ProjectInfo, output_dir: str) -> bool:
        """Compila projeto Python com Nuitka."""
        if not project_info.main_file:
            self.logger.error("Arquivo principal não encontrado")
            return False
        
        main_path = project_info.path / project_info.main_file
        
        cmd = [
            "python", "-m", "nuitka",
            "--onefile",
            "--windows-disable-console",
            f"--output-dir={output_dir}",
            str(main_path),
        ]
        
        self.logger.info(f"Executando Nuitka: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("Nuitka concluído com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Nuitka falhou: {e.stderr}")
            return False


class PkgTool(BaseCompiler):
    """Wrapper para pkg (Node.js)."""
    
    def is_installed(self) -> bool:
        return shutil.which("pkg") is not None
    
    def get_install_url(self) -> str:
        return "https://www.npmjs.com/package/pkg"
    
    def compile(self, project_info: ProjectInfo, output_dir: str) -> bool:
        """Compila projeto Node.js com pkg."""
        if not project_info.main_file:
            self.logger.error("Arquivo principal não encontrado")
            return False
        
        main_path = project_info.path / project_info.main_file
        
        cmd = [
            "pkg",
            str(main_path),
            "--output", str(Path(output_dir) / f"{project_info.name}.exe"),
            "--target", "node18-win-x64",
        ]
        
        self.logger.info(f"Executando pkg: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("pkg concluído com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"pkg falhou: {e.stderr}")
            return False


class DotNetTool(BaseCompiler):
    """Wrapper para dotnet publish."""
    
    def is_installed(self) -> bool:
        return shutil.which("dotnet") is not None
    
    def get_install_url(self) -> str:
        return "https://dotnet.microsoft.com/download"
    
    def compile(self, project_info: ProjectInfo, output_dir: str) -> bool:
        """Publica projeto C# com dotnet publish."""
        csproj_files = list(project_info.path.glob("*.csproj"))
        if not csproj_files:
            self.logger.error("Arquivo .csproj não encontrado")
            return False
        
        cmd = [
            "dotnet", "publish",
            "-c", "Release",
            "-r", "win-x64",
            "--self-contained", "true",
            "-o", output_dir,
            str(csproj_files[0]),
        ]
        
        self.logger.info(f"Executando dotnet publish: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("dotnet publish concluído com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"dotnet publish falhou: {e.stderr}")
            return False


class CompilerManager:
    """
    Gerenciador de múltiplas ferramentas de compilação.
    
    Seleciona e executa a ferramenta apropriada baseada na linguagem do projeto.
    """
    
    TOOLS: Dict[BuildTool, Type[BaseCompiler]] = {
        BuildTool.PYINSTALLER: PyInstallerTool,
        BuildTool.Nuitka: NuitkaTool,
        BuildTool.PKG: PkgTool,
        BuildTool.DOTNET_PUBLISH: DotNetTool,
    }
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._instances: Dict[BuildTool, BaseCompiler] = {}
    
    def get_tool(self, tool: BuildTool) -> Optional[BaseCompiler]:
        """Obtém instância de ferramenta."""
        if tool not in self._instances:
            tool_class = self.TOOLS.get(tool)
            if tool_class:
                self._instances[tool] = tool_class()
        return self._instances.get(tool)
    
    def check_tools(self, tools: List[BuildTool]) -> Dict[BuildTool, bool]:
        """Verifica quais ferramentas estão instaladas."""
        results = {}
        for tool in tools:
            instance = self.get_tool(tool)
            if instance:
                results[tool] = instance.is_installed()
            else:
                results[tool] = False
        return results
    
    def get_best_available_tool(self, recommended_tools: List[BuildTool]) -> Optional[BuildTool]:
        """Retorna a melhor ferramenta disponível."""
        for tool in recommended_tools:
            instance = self.get_tool(tool)
            if instance and instance.is_installed():
                return tool
        return None
    
    def compile_with(self, tool: BuildTool, project_info: ProjectInfo, output_dir: str) -> bool:
        """Compila projeto com ferramenta específica."""
        compiler = self.get_tool(tool)
        
        if not compiler:
            self.logger.error(f"Ferramenta não suportada: {tool}")
            return False
        
        if not compiler.is_installed():
            self.logger.error(f"Ferramenta não instalada: {tool}")
            return False
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        return compiler.compile(project_info, output_dir)
    
    def get_install_instructions(self, tool: BuildTool) -> str:
        """Obtém instruções de instalação para ferramenta."""
        compiler = self.get_tool(tool)
        if compiler:
            return compiler.install_instructions()
        return f"Ferramenta desconhecida: {tool}"
