# Contributing to Knowledge Storage MCP

Thank you for considering contributing to the Knowledge Storage MCP! This document provides guidelines and instructions for contributing to the project.

## Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/AbbyFraenkel/knowledge-storage-mcp-system.git
   cd knowledge-storage-mcp-system
   ```

2. Run the development setup script:
   ```bash
   python setup_dev.py
   ```

   This script will:
   - Create a virtual environment
   - Install dependencies
   - Set up pre-commit hooks
   - Create a `.env` file with development configuration

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Start Neo4j for development:
   ```bash
   docker-compose up -d neo4j
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards described below.

3. Run tests to ensure your changes do not break existing functionality:
   ```bash
   pytest
   ```

4. Lint your code:
   ```bash
   flake8 knowledge_storage_mcp tests
   ```

5. Check type annotations:
   ```bash
   mypy knowledge_storage_mcp
   ```

6. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature X to solve problem Y"
   ```

7. Push your branch to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Create a pull request to the `main` branch.

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide.
- Use 4 spaces for indentation (no tabs).
- Maximum line length is 88 characters (follows Black formatter defaults).
- Use meaningful variable and function names.
- Add docstrings for all modules, classes, and functions.

### Documentation

- Use Google-style docstrings.
- Update README.md and other documentation when adding or changing features.
- Add examples for new APIs.

### Testing

- Write unit tests for all new functionality.
- Maintain or improve test coverage.
- Test edge cases and error handling.

### Commit Messages

- Use clear, descriptive commit messages.
- Start with a verb in the present tense (e.g., "Add", "Fix", "Update").
- Reference issue numbers if applicable.

## Knowledge Schema Contributions

When extending or modifying the knowledge schema:

1. Follow the symbol-concept separation principle.
2. Update both entity and relationship schemas in the `schemas/` directory.
3. Document the changes in the README.md.
4. Add appropriate tests to validate the schema changes.
5. Consider backward compatibility.

## Pull Request Process

1. Update the README.md and documentation with details of changes if applicable.
2. The pull request will be reviewed by at least one maintainer.
3. Address any code review comments or requested changes.
4. Once approved, a maintainer will merge your changes.

## Adding Dependencies

1. Only add necessary dependencies.
2. Update both `requirements.txt` and `requirements-dev.txt` as appropriate.
3. Document why the dependency is needed in your PR description.

## Questions?

If you have any questions about contributing, feel free to open an issue for discussion.

Thank you for your contributions!
