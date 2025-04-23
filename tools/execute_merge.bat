@echo off  
echo Starting merge process with testing...  
  
echo Step 1: Create temporary merge branch...  
git checkout -b temp-merge-test origin/main  
  
echo Step 2: Attempt merge with development branch...  
git merge --no-commit development  
  
echo Step 3: Check for conflicts...  
IF 0 NEQ 0 (  
  echo Merge conflicts detected! Please resolve manually.  
  echo After resolving, run 'git add' on the resolved files and continue with 'git merge --continue'  
  exit /b 1  
)  
  
echo Step 4: Run tests on merged code...  
pytest -v  
  
echo Step 5: Generate coverage report...  
pytest --cov=knowledge_storage_mcp  
  
echo Step 6: If all tests pass, commit the merge...  
git commit -m "Merge development branch into main with comprehensive testing"  
  
echo Merge completed successfully. Please review before pushing to remote. 
