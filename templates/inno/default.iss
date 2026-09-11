; TOSKINSTALLER - Inno Setup Template
; Template para geração de instaladores .EXE
; 
; Copyright (c) 2024 ToskeraLAB ART/TECH House
; Licensed under MIT License

#define MyAppName "{app_name}"
#define MyAppVersion "{app_version}"
#define MyAppPublisher "{app_publisher}"
#define MyAppURL "{app_url}"
#define MyAppExeName "{app_exe}"

[Setup]
AppId={{{#MyAppName}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={{pf}}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir={output_dir}
OutputBaseFilename={#MyAppName}_Setup_{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.ism"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.ism"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: {create_desktop}
Name: "startmenuicon"; Description: "{{cm:CreateStartMenuIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: {create_startmenu}

[Files]
Source: "{tmp}\app\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Apps parceiros (se houver)
{partners_section}

[Icons]
Name: "{{group}}\{#MyAppName}"; Filename: "{{app}}\{#MyAppExeName}}"
Name: "{{autodesktop}}\{#MyAppName}"; Filename: "{{app}}\{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userprograms}}\{#MyAppName}"; Filename: "{{app}}\{#MyAppExeName}}"; Tasks: startmenuicon

[Run]
Filename: "{{app}}\{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  WelcomePage: TWizardPage;
  LicensePage: TWizardPage;

procedure InitializeWizard;
begin
  // Página de boas-vindas customizada
  WelcomePage := CreateCustomPage(wpWelcome, 
    '{app_name}', 
    'Bem-vindo ao assistente de instalação');
  
  // Página de licença customizada  
  LicensePage := CreateCustomPage(wpLicense, 
    'Contrato de Licença', 
    'Por favor, leia o contrato abaixo');
  
  // Configurar texto da licença
  with TNewMemo.Create(WizardForm) do
  begin
    Parent := LicensePage.Surface;
    Left := 10;
    Top := 10;
    Width := LicensePage.SurfaceWidth - 20;
    Height := LicensePage.SurfaceHeight - 20;
    ReadOnly := True;
    ScrollBars := ssVertical;
    Text := '{license_text}';
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  // Ações específicas por página
  if CurPageID = wpReady then
  begin
    // Página final pronta
  end;
end;

procedure DeinitializeSetup;
begin
  // Limpeza pós-instalação
end;
