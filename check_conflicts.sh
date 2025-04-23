#!/bin/bash  
echo "Checking for potential merge conflicts..."  
  
# Create a temporary branch for testing  
git checkout -b temp-conflict-test  
  
# Try to merge without committing  
echo "Attempting dry-run merge..."  
git merge --no-commit --no-ff development  
  
# Check if there were conflicts  
if [ $? -ne 0 ]; then  
  echo "Conflicts detected! The following files have conflicts:"  
  git diff --name-only --diff-filter=U  
else  
  echo "No direct conflicts detected in the merge."  
fi  
  
# Abort the merge to keep the branch clean  
git merge --abort  
  
echo "Conflict check complete." 
