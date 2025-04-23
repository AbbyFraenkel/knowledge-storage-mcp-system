@echo off  
echo Creating consolidated pull request for repository merge...  
  
rem Ensure we have the latest from all branches  
echo Fetching latest changes...  
git fetch --all  
  
rem Checkout the merge-analysis branch where our strategy documents are  
git checkout merge-analysis  
  
rem Create a new consolidation branch  
set BRANCH_NAME=consolidation-4/02  
echo Creating consolidation branch: %BRANCH_NAME%  
git checkout -b %BRANCH_NAME%  
  
rem Add PR template directory  
echo Adding PR template...  
mkdir .github\PULL_REQUEST_TEMPLATE  
  
rem Commit the consolidation preparation  
git add .  
git commit -m "Prepare consolidation pull request"  
  
rem Provide instructions for next steps  
echo.  
echo ====================================================  
echo Consolidation branch prepared successfully!  
echo Next steps:  
echo 1. Review the analysis results  
echo 2. Run 'git push -u origin %%BRANCH_NAME%%'  
echo 3. Create a pull request on GitHub  
echo ==================================================== 
