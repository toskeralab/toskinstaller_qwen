# TOSKINSTALLER

**Desenvolvido por:** ToskeraLAB ART/TECH House

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)](https://pypi.org/project/PySide6/)

## 📦 O que é o TOSKINSTALLER?

O **TOSKINSTALLER** é uma ferramenta portátil para Windows que permite empacotar aplicativos em instaladores profissionais (.EXE, .MSI) ou versões portables, com interface customizável e suporte a múltiplas linguagens de programação.

### ✨ Funcionalidades Principais

- **Detecção Automática de Linguagem**: Identifica projetos Python, Node.js, C# e mais
- **Múltiplas Ferramentas de Compilação**: Suporta PyInstaller, Nuitka, pkg, dotnet publish
- **Formatos de Saída Múltiplos**: Gere .EXE (Inno Setup), .MSI (WiX Toolset) e Portable simultaneamente
- **UI Customizável**: 5 temas de animação, seletor de cores, upload de logo e banners
- **Apps Parceiros**: Instale dependências adicionais (VC++ Redist, .NET Runtime, etc.)
- **Internacionalização**: PT-BR e EN
- **Assinatura Digital**: Suporte opcional a certificados .pfx

## 🚀 Quick Start

### Pré-requisitos

- Windows 10/11 (x64 recomendado)
- Python 3.11 ou superior
- Git (para clonar o repositório)

### Instalação para Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/toskeralab/toskinstaller_qwen.git
cd toskinstaller_qwen

# Crie um ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute o TOSKINSTALLER
python src/main.py
```

### Build do Executável Portátil

O TOSKINSTALLER oferece **duas opções** de compilação. Recomenda-se testar primeiro em modo desenvolvimento (`python src/main.py`).

#### Opção 1: Nuitka (Recomendado)

```bash
# Instalar dependências de build
pip install -r requirements-dev.txt

# Executar build com Nuitka
python build_toskinstaller.py --nuitka

# O executável será gerado em: dist/ToskInstaller.exe
```

**Vantagens do Nuitka:**
- ✅ Compilação para C++ (mais rápido em runtime)
- ✅ Ofuscação de código nativa
- ✅ Menor taxa de falsos positivos em antivírus
- ✅ Melhor performance com UI Qt

#### Opção 2: PyInstaller (Alternativa)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Executar build
pyinstaller --onefile --windowed --name=ToskInstaller src/main.py

# O executável será gerado em: dist/ToskInstaller.exe
```

**Vantagens do PyInstaller:**
- ✅ Mais maduro e testado
- ✅ Build mais rápido (1-3 min vs 5-15 min do Nuitka)
- ✅ Melhor compatibilidade com bibliotecas complexas
- ✅ Fácil depuração

#### Troubleshooting Comum

**Erro: Módulo não encontrado**
```bash
pip install -r requirements.txt --upgrade
rm -rf dist/ build/ __pycache__/
python build_toskinstaller.py --nuitka
```

**Antivírus bloqueando o executável**
- Assine digitalmente o executável (configurável no próprio TOSKINSTALLER)
- Adicione exceção no antivírus para a pasta `dist/`
- Use Nuitka em vez de PyInstaller (menor detecção)

**Tamanho muito grande (>200MB)**
```bash
# Usar compressão UPX com Nuitka
python build_toskinstaller.py --nuitka --enable-plugin=upx
```

## 📖 Documentação

- [Guia do Usuário (PT-BR)](docs/USER_GUIDE_PT.md)
- [User Guide (EN)](docs/USER_GUIDE_EN.md)
- [Instruções de Build](docs/BUILD_INSTRUCTIONS.md)
- [Guia do Desenvolvedor](docs/DEVELOPER_GUIDE.md)

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia |
|------------|------------|
| Linguagem | Python 3.11+ |
| UI Framework | PySide6 (Qt for Python) |
| Build Tool | Nuitka / PyInstaller |
| Empacotamento EXE | Inno Setup |
| Empacotamento MSI | WiX Toolset |
| Empacotamento Portable | 7-Zip + Stub Python |

## 📋 Linguagens e Ferramentas Suportadas

| Linguagem | Ferramentas de Conversão |
|-----------|-------------------------|
| Python | PyInstaller, Nuitka, cx_Freeze |
| Node.js | pkg, electron-builder |
| C# (.NET) | dotnet publish, MSBuild |

## 🎯 Fluxo de Uso

1. **Selecione o Projeto**: Aponte para a pasta do seu projeto
2. **Detecção Automática**: O TOSKINSTALLER identifica a linguagem e ferramentas necessárias
3. **Verificação de Dependências**: Se necessário, orienta instalação das ferramentas
4. **Configuração do Pacote**: Escolha formatos (.EXE, .MSI, Portable), customize UI, apps parceiros
5. **Geração**: O TOSKINSTALLER converte e empacota tudo em um único executável

## 📁 Estrutura do Projeto

```
toskinstaller_qwen/
├── src/                  # Código-fonte principal
│   ├── core/             # Lógica de detecção e compilação
│   ├── ui/               # Interface PySide6
│   ├── engines/          # Motores de empacotamento
│   ├── tools/            # Wrappers de ferramentas externas
│   └── models/           # Modelos de dados
├── templates/            # Templates de instaladores
├── tests/                # Testes unitários
├── docs/                 # Documentação
├── assets/               # Recursos visuais
└── build_toskinstaller.py # Script de build
```

## 🔧 Ferramentas Externas Requeridas

O TOSKINSTALLER pode baixar e instalar automaticamente:

- **Inno Setup**: Para gerar instaladores .EXE
- **WiX Toolset**: Para gerar instaladores .MSI
- **7-Zip**: Para compactação em modo portable

Para conversão de projetos:
- **PyInstaller/Nuitka**: Projetos Python
- **pkg**: Projetos Node.js
- **(.NET SDK**: Projetos C#

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🏷️ Marca

**ToskeraLAB ART/TECH House** © 2024

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia o [Guia do Desenvolvedor](docs/DEVELOPER_GUIDE.md) antes de enviar PRs.

## 📞 Contato

- Website: [toskeralab.com](https://toskeralab.com)
- Email: contact@toskeralab.com

---

*Facilidade de uso (50%) • Performance (25%) • Tamanho do executável (25%)*
