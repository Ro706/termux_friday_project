#!/bin/bash

# Friday AI Assistant Setup Script
# Works on Linux and Termux (Android)

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Friday AI Assistant Setup...${NC}"

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed.${NC}"
    exit 1
fi

# 2. Check for Pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}Warning: pip3 is not installed. Attempting to install...${NC}"
    if [ -n "$TERMUX_VERSION" ]; then
        pkg install python-pip -y
    else
        sudo apt-get update && sudo apt-get install python3-pip -y
    fi
fi

# 3. Handle Termux Specific Dependencies
if [ -n "$TERMUX_VERSION" ]; then
    echo -e "${YELLOW}Detected Termux environment. Installing system dependencies...${NC}"
    pkg update && pkg upgrade -y
    pkg install libjpeg-turbo libpng -y
    pkg install termux-api -y
fi

# 4. Install Python Dependencies
echo -e "${GREEN}Installing Python dependencies from requirements.txt...${NC}"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# 5. Create .env template if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env template...${NC}"
    cat <<EOF > .env
USERNAME="User"
GROQ_API_KEY=""
COHERE_API_KEY=""
SENDER_EMAIL=""
EMAIL_PASSWORD=""
HUGGINGFACE_API_KEY=""
OPENWEATHER_API_KEY=""
NEWS_API=""
EOF
    echo -e "${GREEN}.env file created. Please open it and add your API keys.${NC}"
else
    echo -e "${YELLOW}.env file already exists. Skipping creation.${NC}"
fi

# 6. Final Instructions
echo -e "${GREEN}--------------------------------------------------${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "1. Edit the ${YELLOW}.env${NC} file with your actual API keys."
echo -e "2. Run the assistant using: ${YELLOW}python main.py${NC}"
echo -e "${GREEN}--------------------------------------------------${NC}"
