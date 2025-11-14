#!/bin/bash
# One-line installer for Context Engine MCP Server
# Usage: curl -fsSL https://raw.githubusercontent.com/USER/REPO/main/install.sh | bash

set -e

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║        Context Engine MCP Server - Easy Installer                   ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}[1/6]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo -e "${YELLOW}Python 3.8+ required. Found: $python_version${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $(python3 --version 2>&1 | awk '{print $2}') found"

# Install location
INSTALL_DIR="$HOME/.context-engine"
echo ""
echo -e "${BLUE}[2/6]${NC} Installation directory: ${INSTALL_DIR}"

# Create installation directory
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Existing installation found. Updating...${NC}"
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download or clone repository
echo ""
echo -e "${BLUE}[3/6]${NC} Downloading Context Engine..."

# Check if git is available
if command -v git &> /dev/null; then
    git clone https://github.com/svsairevanth12/contextengine.git . 2>/dev/null || {
        echo -e "${YELLOW}Git clone failed. Downloading as zip...${NC}"
        # Fallback to downloading zip
        if command -v curl &> /dev/null; then
            curl -L https://github.com/svsairevanth12/contextengine/archive/refs/heads/claude/easy-mcp-install-01QbCguyLeCXRbad4kkgC7hD.zip -o repo.zip
            unzip -q repo.zip
            mv contextengine-*/* .
            rm -rf contextengine-* repo.zip
        else
            echo -e "${YELLOW}curl not found. Please install git or curl.${NC}"
            exit 1
        fi
    }
    # Checkout the easy install branch
    git checkout claude/easy-mcp-install-01QbCguyLeCXRbad4kkgC7hD 2>/dev/null || true
else
    # Use curl to download
    if command -v curl &> /dev/null; then
        curl -L https://github.com/svsairevanth12/contextengine/archive/refs/heads/claude/easy-mcp-install-01QbCguyLeCXRbad4kkgC7hD.zip -o repo.zip
        unzip -q repo.zip
        mv contextengine-*/* .
        rm -rf contextengine-* repo.zip
    else
        echo -e "${YELLOW}git or curl required for installation.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} Downloaded"

# Create virtual environment
echo ""
echo -e "${BLUE}[4/6]${NC} Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install package
echo ""
echo -e "${BLUE}[5/6]${NC} Installing dependencies (this may take a few minutes)..."
pip install --quiet --upgrade pip
pip install --quiet -e .

# Download embedding model
echo ""
echo -e "${BLUE}[6/6]${NC} Downloading embedding model (one-time, ~80MB)..."
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" 2>/dev/null

echo ""
echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""

# Create activation script
cat > "$INSTALL_DIR/activate-mcp.sh" << 'EOF'
#!/bin/bash
cd "$HOME/.context-engine"
source venv/bin/activate
export CONTEXT_ENGINE_HOME="$HOME/.context-engine"
EOF

chmod +x "$INSTALL_DIR/activate-mcp.sh"

# Detect OS for config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    MCP_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    MCP_CONFIG_FILE="$MCP_CONFIG_DIR/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    MCP_CONFIG_DIR="$HOME/.config/Claude"
    MCP_CONFIG_FILE="$MCP_CONFIG_DIR/claude_desktop_config.json"
else
    # Windows (Git Bash or WSL)
    MCP_CONFIG_DIR="$APPDATA/Claude"
    MCP_CONFIG_FILE="$MCP_CONFIG_DIR/claude_desktop_config.json"
fi

# Create config directory if it doesn't exist
mkdir -p "$MCP_CONFIG_DIR"

# Generate MCP configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}MCP Server Configuration:${NC}"
echo ""
echo "Add this to your Claude Desktop config file:"
echo -e "${YELLOW}$MCP_CONFIG_FILE${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create config snippet
cat << EOF
{
  "mcpServers": {
    "context-engine": {
      "command": "$INSTALL_DIR/venv/bin/python",
      "args": ["$INSTALL_DIR/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "REPLACE_WITH_YOUR_PROJECT_PATH"
      }
    }
  }
}
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save config to file
cat << EOF > "$INSTALL_DIR/mcp-config-snippet.json"
{
  "mcpServers": {
    "context-engine": {
      "command": "$INSTALL_DIR/venv/bin/python",
      "args": ["$INSTALL_DIR/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "REPLACE_WITH_YOUR_PROJECT_PATH"
      }
    }
  }
}
EOF

echo -e "${GREEN}Config snippet saved to:${NC} $INSTALL_DIR/mcp-config-snippet.json"
echo ""

# Offer to configure automatically
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo -e "${BLUE}Existing Claude Desktop config found.${NC}"
    read -p "Would you like to auto-configure? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter path to your codebase: " CODEBASE_PATH

        # Backup existing config
        cp "$MCP_CONFIG_FILE" "$MCP_CONFIG_FILE.backup"

        # Add our config (simple merge - assumes valid JSON)
        python3 << PYTHON
import json
config_file = "$MCP_CONFIG_FILE"
try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {}

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['context-engine'] = {
    "command": "$INSTALL_DIR/venv/bin/python",
    "args": ["$INSTALL_DIR/mcp_server.py"],
    "env": {
        "CODEBASE_PATH": "$CODEBASE_PATH"
    }
}

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✓ Configuration updated!")
PYTHON

        echo ""
        echo -e "${GREEN}✓ Claude Desktop configured!${NC}"
        echo -e "${YELLOW}Please restart Claude Desktop for changes to take effect.${NC}"
    fi
else
    echo -e "${YELLOW}Claude Desktop config not found at: $MCP_CONFIG_FILE${NC}"
    echo "You'll need to create it manually with the snippet above."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}Installation Summary:${NC}"
echo ""
echo "  Installation directory: $INSTALL_DIR"
echo "  Config snippet:         $INSTALL_DIR/mcp-config-snippet.json"
echo "  Activation script:      $INSTALL_DIR/activate-mcp.sh"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo ""
echo "  1. Edit your Claude Desktop config (or use snippet above)"
echo "  2. Replace CODEBASE_PATH with your project path"
echo "  3. Restart Claude Desktop"
echo "  4. Look for 🔌 icon in Claude"
echo "  5. Ask Claude to search your codebase!"
echo ""
echo -e "${BLUE}CLI Tool:${NC}"
echo ""
echo "  source $INSTALL_DIR/activate-mcp.sh"
echo "  python main.py index ./your_project"
echo "  python main.py interactive"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🎉 Happy coding with context! 🎉${NC}"
echo ""
