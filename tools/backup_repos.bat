@echo off  
echo Creating backups of repositories before consolidation...  
  
rem Create backup directory  
set BACKUP_DIR=..\knowledge-storage-backups\4/02  
mkdir %BACKUP_DIR%  
  
rem Backup main repository  
echo Backing up knowledge-storage-mcp...  
git bundle create %BACKUP_DIR%\knowledge-storage-mcp.bundle --all  
  
rem Backup archived repositories  
echo Backing up archived repositories...  
xcopy /E /I /Y "..\archive-knowledge-storage-mcp-v1" "%BACKUP_DIR%\archive-knowledge-storage-mcp-v1"  
xcopy /E /I /Y "..\archive-knowledge-storage-mcp-prototype" "%BACKUP_DIR%\archive-knowledge-storage-mcp-prototype"  
  
echo Backups completed in %BACKUP_DIR% 
