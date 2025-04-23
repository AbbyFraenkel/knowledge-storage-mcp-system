@echo off  
echo Knowledge Storage MCP Repository Consolidation Tools  
echo ===========================================  
  
if "%1"=="" goto help  
  
if "%1"=="analyze-diff" goto analyze_diff  
if "%1"=="check-conflicts" goto check_conflicts  
if "%1"=="backup" goto backup  
if "%1"=="prepare-merge" goto prepare_merge  
if "%1"=="execute-merge" goto execute_merge  
if "%1"=="help" goto help  
  
echo Unknown command: %1  
goto help  
  
:analyze_diff  
echo Analyzing differences between branches...  
python tools\compare_files.py  
goto end  
  
:check_conflicts  
echo Checking for potential merge conflicts...  
call tools\check_conflicts.bat  
goto end  
  
:backup  
echo Creating backups of repositories...  
call tools\backup_repos.bat  
goto end  
  
:prepare_merge  
echo Preparing consolidation pull request...  
call tools\create_consolidation_pr.bat  
goto end  
  
:execute_merge  
echo Executing merge with testing...  
call tools\execute_merge.bat  
goto end  
  
:help  
echo Available commands:  
echo   analyze-diff    : Analyze differences between branches  
echo   check-conflicts : Check for potential merge conflicts  
echo   backup          : Create backups of repositories  
echo   prepare-merge   : Prepare consolidation pull request  
echo   execute-merge   : Execute the merge after preparation  
echo   help            : Show this help message  
  
:end 
