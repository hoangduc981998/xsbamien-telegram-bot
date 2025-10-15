# Multi-stage build for smaller image size
FROM python:3.12-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# Copy dependencies from builder
COPY --from=builder --chown=botuser:botuser /root/.local /home/botuser/.local

# Copy application code
COPY --chown=botuser:botuser . .

# Set PATH for user-installed packages
ENV PATH=/home/botuser/.local/bin:$PATH

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Switch to non-root user
USER botuser

# Run bot
CMD ["python", "-m", "app.main"]
