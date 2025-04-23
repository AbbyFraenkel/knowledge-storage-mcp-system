#!/bin/bash  
echo "Creating consolidated pull request for repository merge..."  
  
# Ensure we have the latest from all branches  
echo "Fetching latest changes..."  
git fetch --all  
  
# Checkout the merge-analysis branch where our strategy documents are  
git checkout merge-analysis  
  
# Create a new consolidation branch  
BRANCH_NAME="consolidation-$(date +%%Y%%m%%d)"  
echo "Creating consolidation branch: $BRANCH_NAME"  
git checkout -b $BRANCH_NAME  
  
# Copy merge strategy and test plans to the branch  
echo "Adding merge strategy documents..."  
git checkout merge-analysis -- MERGE_STRATEGY.md TEST_PLAN.md 
  
# Add PR template directory  
echo "Adding PR template..."  
mkdir -p .github/PULL_REQUEST_TEMPLATE  
git checkout merge-analysis -- .github/PULL_REQUEST_TEMPLATE/merge_request.md  
  
# Commit the consolidation preparation  
git add .  
git commit -m "Prepare consolidation pull request"  
  
# Provide instructions for next steps  
echo ""  
echo "===================================================="  
echo "Consolidation branch prepared successfully!"  
echo "Next steps:"  
echo "1. Review the analysis results"  
echo "2. Run 'git push -u origin $BRANCH_NAME'"  
echo "3. Create a pull request on GitHub"  
echo "====================================================" 
