FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY knowledge_storage_mcp/ /app/knowledge_storage_mcp/
COPY schemas/ /app/schemas/
COPY pyproject.toml .

# Create non-root user
RUN addgroup --system mcp && \
    adduser --system --group mcp && \
    chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "knowledge_storage_mcp.server"]