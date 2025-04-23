# Makefile for repository consolidation  
  
.PHONY: analyze-diff check-conflicts backup prepare-merge execute-merge test  
  
# Default target shows help  
help:  
	@echo "Makefile for repository consolidation"  
	@echo ""  
	@echo "Available targets:"  
	@echo "  analyze-diff    : Analyze differences between branches"  
	@echo "  check-conflicts : Check for potential merge conflicts"  
	@echo "  backup          : Create backups of repositories"  
	@echo "  prepare-merge   : Prepare consolidation pull request"  
	@echo "  execute-merge   : Execute the merge after preparation"  
	@echo "  test            : Run tests on the merged code"  
  
# Analyze differences between branches  
analyze-diff:  
	python compare_files.py  
  
# Check for potential merge conflicts  
check-conflicts:  
	bash check_conflicts.sh  
  
# Create backups of repositories  
backup:  
	bash backup_repos.sh  
  
# Prepare consolidation pull request  
prepare-merge:  
	bash create_consolidation_pr.sh  
  
# Execute the merge  
execute-merge:  
	bash execute_merge.sh  
  
# Run tests on the merged code  
test:  
	pytest -v  
	pytest --cov=knowledge_storage_mcp 
