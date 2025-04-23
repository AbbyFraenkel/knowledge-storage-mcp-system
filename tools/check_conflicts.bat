@echo off  
echo Checking for potential merge conflicts...  
  
rem Create a temporary branch for testing  
git checkout -b temp-conflict-test  
  
rem Try to merge without committing  
echo Attempting dry-run merge...  
git merge --no-commit --no-ff development  
  
rem Check if there were conflicts  
IF 0 NEQ 0 (  
  echo Conflicts detected! The following files have conflicts:  
  git diff --name-only --diff-filter=U  
) ELSE (  
  echo No direct conflicts detected in the merge.  
)  
  
rem Abort the merge to keep the branch clean  
git merge --abort  
  
echo Conflict check complete. 
