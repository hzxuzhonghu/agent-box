# Browser-use Sandbox Dockerfile
# This creates an isolated environment for browser automation using Playwright

FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /workspace

# Install system dependencies for Playwright and browsers
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl \
    wget \
    git \
    openssh-server \
    sudo \
    # Browser dependencies for Chromium/Chrome
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    # Additional libraries
    libx11-xcb1 \
    libxcb-dri3-0 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Create sandbox user
RUN useradd -m -s /bin/bash sandbox && \
    echo "sandbox:sandbox" | chpasswd && \
    usermod -aG sudo sandbox && \
    echo "sandbox ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install Python packages
RUN pip install --no-cache-dir \
    playwright \
    playwright-stealth \
    requests \
    pillow

# Install Playwright browsers and system dependencies (as root)
# This installs to /root/.cache/ms-playwright
RUN playwright install chromium && \
    playwright install firefox && \
    playwright install webkit && \
    playwright install-deps

# Make browsers accessible to all users by setting up a shared location
RUN mkdir -p /ms-playwright && \
    cp -r /root/.cache/ms-playwright/* /ms-playwright/ && \
    chmod -R 755 /ms-playwright

# Set up SSH for remote access (optional, for sandbox API compatibility)
RUN mkdir -p /var/run/sshd && \
    mkdir -p /home/sandbox/.ssh && \
    chmod 700 /home/sandbox/.ssh && \
    chown -R sandbox:sandbox /home/sandbox/.ssh

# Configure SSH to allow password authentication
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

# Switch to sandbox user
USER sandbox
WORKDIR /home/sandbox

# Set environment variables to use shared browser location
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Expose SSH port (if using sandbox API with SSH tunnel)
EXPOSE 22

# Default command - keep container running
CMD ["bash", "-c", "sudo service ssh start && tail -f /dev/null"]
