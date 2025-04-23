@echo off  
echo Analyzing differences between main and development branches...  
  
echo ===============================================  
echo Creating detailed file diff report...  
git diff origin/main development --name-status  
  
echo Checking for potential merge conflicts...  
git merge-tree $(git merge-base origin/main development) origin/main development  
  
echo Generating detailed diffs for critical files...  
git diff origin/main:knowledge_storage_mcp/server.py development:knowledge_storage_mcp/server.py  
git diff origin/main:knowledge_storage_mcp/db/connection.py development:knowledge_storage_mcp/db/connection.py  
git diff origin/main:knowledge_storage_mcp/api/relationships.py development:knowledge_storage_mcp/api/relationships.py  
  
echo Analysis complete. See diff_report.txt, conflict_analysis.txt, and *_diff.txt files for details. 
