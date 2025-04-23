#!/usr/bin/env python  
""">> compare_files.py && echo File Comparison Tool for Repository Consolidation>> compare_files.py && echo. >> compare_files.py && echo This script analyzes the differences between the main and development branches>> compare_files.py && echo to identify files that need careful review during merging.>> compare_files.py && echo """
  
import os 
import subprocess 
import json 
from collections import defaultdict 
  
def run_command(command): 
    """Run a shell command and return the output""" 
    result = subprocess.run(command, shell=True, capture_output=True, text=True) 
    return result.stdout.strip()
  
def get_changed_files(): 
    """Get list of files changed between main and development""" 
    output = run_command('git diff --name-status origin/main development') 
ECHO is on.
    changes = { 
        'added': [], 
        'modified': [], 
        'deleted': [] 
    } 
ECHO is on.
    for line in output.split('\n'): 
        if not line.strip(): 
            continue 
ECHO is on.
        parts = line.split('\t') 
        status = parts[0] 
        filename = parts[1] 
ECHO is on.
        if status.startswith('A'): 
            changes['added'].append(filename) 
        elif status.startswith('M'): 
            changes['modified'].append(filename) 
        elif status.startswith('D'): 
            changes['deleted'].append(filename) 
ECHO is on.
    return changes
  
def analyze_critical_files(critical_files): 
    """Analyze critical files for detailed differences""" 
    results = {} 
ECHO is on.
    for filepath in critical_files: 
        if os.path.exists(filepath): 
            # Check if file exists in both branches 
"0"') 
"0"') 
ECHO is on.
            if main_exists == '1' and dev_exists == '1': 
                # File exists in both branches, analyze differences 
                diff = run_command(f'git diff origin/main:"{filepath}" development:"{filepath}"') 
ECHO is on.
                if diff: 
                    results[filepath] = { 
                        'status': 'modified', 
                        'diff_lines': len(diff.split('\n')), 
                        'recommendation': 'manual review' if len(diff.split('\n'))  else 'auto-merge may be safe' 
                    } 
                else: 
                    results[filepath] = { 
                        'status': 'identical', 
                        'recommendation': 'safe to merge' 
                    } 
            elif main_exists == '1': 
                results[filepath] = { 
                    'status': 'deleted in development', 
                    'recommendation': 'investigate deletion reason' 
                } 
            elif dev_exists == '1': 
                results[filepath] = { 
                    'status': 'added in development', 
                    'recommendation': 'review new file' 
                } 
        else: 
            results[filepath] = { 
                'status': 'does not exist locally', 
                'recommendation': 'check branch content' 
            } 
ECHO is on.
    return results
def main():  
    """Main function to run the analysis"""  
    print("Analyzing differences between branches...")  
ECHO is on.
    # Get all changed files  
    changes = get_changed_files()  
ECHO is on.
    # Critical files that need special attention  
    critical_files = [  
        'knowledge_storage_mcp/server.py',   
        'knowledge_storage_mcp/db/connection.py',  
        'knowledge_storage_mcp/api/relationships.py'  
    ]  
ECHO is on.
    # Add any deleted Python files as they might contain important functionality  
    critical_files.extend([f for f in changes['deleted'] if f.endswith('.py')])  
ECHO is on.
    # Analyze critical files  
    file_analysis = analyze_critical_files(critical_files) 
    # Generate report  
    report = {  
        'summary': {  
            'added': len(changes['added']),  
            'modified': len(changes['modified']),  
            'deleted': len(changes['deleted'])  
        },  
        'critical_files': file_analysis,  
        'recommendations': []  
    }  
ECHO is on.
    # Output summary to console  
    print(f"\nSummary:")  
    print(f"- {report['summary']['added']} files added")  
    print(f"- {report['summary']['modified']} files modified")  
    print(f"- {report['summary']['deleted']} files deleted")  
ECHO is on.
    print("\nCritical File Analysis:")  
    for filepath, analysis in report['critical_files'].items():  
        print(f"- {filepath}: {analysis['status']} - {analysis.get('recommendation', '')}")  
ECHO is on.
if __name__ == "__main__":  
    main() 
