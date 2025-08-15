#!/bin/bash

# KakaoMap Scraping Project Environment Setup
# This script sets up environment variables for the scraping project

echo "Setting up environment variables for KakaoMap scraping project..."

# Get the current directory (project root)
PROJECT_DIR=$(pwd)
echo "Project directory: $PROJECT_DIR"

# Set project-specific environment variables
export KAKAO_PROJECT_DIR="$PROJECT_DIR"
export KAKAO_OUTPUT_DIR="$PROJECT_DIR/output"
export KAKAO_DATA_DIR="$PROJECT_DIR/data"

# Create output and data directories if they don't exist
mkdir -p "$KAKAO_OUTPUT_DIR"
mkdir -p "$KAKAO_DATA_DIR"

# Set Chrome driver options (optional)
export CHROME_HEADLESS="false"  # Set to "true" for headless mode
export CHROME_TIMEOUT="30"

# Set scraping options
export SCRAPING_DELAY="2"  # Delay between requests in seconds
export MAX_RETRIES="3"     # Maximum retry attempts

# Display the set variables
echo ""
echo "Environment variables set:"
echo "KAKAO_PROJECT_DIR: $KAKAO_PROJECT_DIR"
echo "KAKAO_OUTPUT_DIR: $KAKAO_OUTPUT_DIR"
echo "KAKAO_DATA_DIR: $KAKAO_DATA_DIR"
echo "CHROME_HEADLESS: $CHROME_HEADLESS"
echo "CHROME_TIMEOUT: $CHROME_TIMEOUT"
echo "SCRAPING_DELAY: $SCRAPING_DELAY"
echo "MAX_RETRIES: $MAX_RETRIES"
echo ""

# Add to shell profile for permanent setup
SHELL_PROFILE=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_PROFILE="$HOME/.bash_profile"
    if [ ! -f "$SHELL_PROFILE" ]; then
        SHELL_PROFILE="$HOME/.bashrc"
    fi
fi

if [ -n "$SHELL_PROFILE" ]; then
    echo "To make these variables permanent, add the following to $SHELL_PROFILE:"
    echo ""
    echo "# KakaoMap Scraping Project Environment Variables"
    echo "export KAKAO_PROJECT_DIR=\"$PROJECT_DIR\""
    echo "export KAKAO_OUTPUT_DIR=\"$PROJECT_DIR/output\""
    echo "export KAKAO_DATA_DIR=\"$PROJECT_DIR/data\""
    echo "export CHROME_HEADLESS=\"$CHROME_HEADLESS\""
    echo "export CHROME_TIMEOUT=\"$CHROME_TIMEOUT\""
    echo "export SCRAPING_DELAY=\"$SCRAPING_DELAY\""
    echo "export MAX_RETRIES=\"$MAX_RETRIES\""
    echo ""
    echo "Then run: source $SHELL_PROFILE"
fi

echo "Environment setup complete!" 