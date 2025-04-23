@echo off  
echo Running tests for consolidated repository...  
  
echo Checking if pytest is installed...  
python -m pytest --version  
if 0 NEQ 0 (  
  echo Error: pytest is not installed. Please run 'pip install pytest pytest-cov'  
  exit /b 1  
)  
  
echo Running tests...  
python -m pytest -v  
  
echo Generating coverage report...  
python -m pytest --cov=knowledge_storage_mcp  
  
if 0 NEQ 0 (  
  echo Tests failed! Please fix the issues before proceeding with the merge.  
  exit /b 1  
) else (  
  echo All tests passed successfully!  
) 
