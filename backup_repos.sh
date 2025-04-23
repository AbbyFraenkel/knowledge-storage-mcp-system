#!/bin/bash  
echo "Creating backups of repositories before consolidation..."  
  
# Create backup directory  
BACKUP_DIR="../knowledge-storage-backups/$(date +%%Y%%m%%d)"  
mkdir -p $BACKUP_DIR  
  
# Backup main repository  
echo "Backing up knowledge-storage-mcp..."  
git bundle create $BACKUP_DIR/knowledge-storage-mcp.bundle --all  
  
# Backup archived repositories  
echo "Backing up archived repositories..."  
cp -r "../archive-knowledge-storage-mcp-v1" $BACKUP_DIR/  
cp -r "../archive-knowledge-storage-mcp-prototype" $BACKUP_DIR/  
  
echo "Backups completed in $BACKUP_DIR" 
