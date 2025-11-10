
; MediaCrawler GUI 安装脚本
!define APP_NAME "MediaCrawler GUI"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "MediaCrawler Team"
!define APP_EXE "MediaCrawler-GUI.exe"

Name "${APP_NAME}"
OutFile "MediaCrawler-GUI-Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"

Page directory
Page instfiles

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File /r "dist\*.*"
    
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\${APP_NAME}\*.*"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\${APP_NAME}.lnk"
SectionEnd
