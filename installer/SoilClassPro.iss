#define MyAppName "SoilClass Pro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Batuhan Baris Doger, Erol Boz, Furkan Kagan Ekici"
#define MyAppExeName "SoilClassPro.exe"

[Setup]
AppId={{6E9F9B0E-9C7D-4E20-9F0B-2B6E6B9C3E41}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SoilClassPro
DefaultGroupName=SoilClass Pro
DisableProgramGroupPage=yes
OutputDir=..\installer_output
OutputBaseFilename=SoilClassPro_Setup_{#MyAppVersion}
SetupIconFile=..\soilclass\assets\logo.ico
LicenseFile=..\LICENSE
VersionInfoVersion={#MyAppVersion}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\SoilClassPro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  SettingsDir, SettingsFile, LangCode: String;
begin
  if CurStep = ssPostInstall then
  begin
    if ActiveLanguage = 'turkish' then
      LangCode := 'tr'
    else
      LangCode := 'en';

    SettingsDir := ExpandConstant('{%USERPROFILE}\.soilclasspro');
    SettingsFile := SettingsDir + '\settings.json';

    if not FileExists(SettingsFile) then
    begin
      ForceDirectories(SettingsDir);
      SaveStringToFile(SettingsFile,
        '{' + #13#10 +
        '  "language": "' + LangCode + '"' + #13#10 +
        '}', False);
    end;
  end;
end;
