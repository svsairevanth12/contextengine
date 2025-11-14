# Easy Installation Guide

Get Context Engine MCP server running in **under 5 minutes**! 🚀

## 🎯 One-Line Install (Recommended)

### macOS / Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/svsairevanth12/contextengine/claude/easy-mcp-install-01QbCguyLeCXRbad4kkgC7hD/install.sh | bash
```

### What it does:
- ✅ Checks Python 3.8+
- ✅ Downloads Context Engine
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Downloads embedding model
- ✅ Generates MCP config
- ✅ Optionally auto-configures Claude Desktop

**That's it!** Just follow the prompts.

---

## 📋 Manual Installation (5 minutes)

### Step 1: Download

```bash
# Clone the repository
git clone https://github.com/svsairevanth12/contextengine.git
cd contextengine

# Checkout the easy install branch
git checkout claude/easy-mcp-install-01QbCguyLeCXRbad4kkgC7hD
```

### Step 2: Install

```bash
# Run the install script
./install.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -e .

# Download model (one-time)
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Step 3: Configure MCP

**Option A: Auto-configure**
```bash
python configure-mcp.py /path/to/your/project
```

**Option B: Manual config**

1. Find your Claude Desktop config:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2. Add this (replace paths):
```json
{
  "mcpServers": {
    "context-engine": {
      "command": "/path/to/contextengine/venv/bin/python",
      "args": ["/path/to/contextengine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "/path/to/your/project"
      }
    }
  }
}
```

3. Restart Claude Desktop

---

## 🔗 Share with Others

### Method 1: Share the install script URL

Send this one-liner:
```bash
curl -fsSL https://raw.githubusercontent.com/svsairevanth12/contextengine/claude/easy-mcp-install-01QbCguyLeCXRbad4kkgC7hD/install.sh | bash
```

### Method 2: Share the config snippet

After installation, you can share the generated config:

**Location:** `~/.context-engine/mcp-config-snippet.json`

Or generate fresh config:
```bash
python configure-mcp.py
```

Send them this config (they just need to change the CODEBASE_PATH):

```json
{
  "mcpServers": {
    "context-engine": {
      "command": "/Users/USERNAME/.context-engine/venv/bin/python",
      "args": ["/Users/USERNAME/.context-engine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "REPLACE_WITH_YOUR_PROJECT_PATH"
      }
    }
  }
}
```

### Method 3: Share as GitHub Gist

1. Generate your config:
   ```bash
   python configure-mcp.py > mcp-config.json
   ```

2. Create GitHub Gist:
   - Go to https://gist.github.com
   - Paste the config
   - Name it: `context-engine-mcp-config.json`
   - Share the URL!

---

## 🚀 Quick Start After Installation

### 1. Test CLI Tool

```bash
# Activate environment
source ~/.context-engine/venv/bin/activate

# Index your project
python main.py index ./your_project

# Try interactive mode
python main.py interactive
```

### 2. Use with Claude Desktop

1. **Restart Claude Desktop** completely
2. **Look for 🔌 icon** in the interface
3. **Ask Claude:** "Search the codebase for authentication"
4. **Watch Claude** call the MCP tools!

---

## 🎨 Example Configurations

### For a Single Project:

```json
{
  "mcpServers": {
    "context-engine": {
      "command": "/Users/yourname/.context-engine/venv/bin/python",
      "args": ["/Users/yourname/.context-engine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "/Users/yourname/projects/myapp"
      }
    }
  }
}
```

### For Multiple Projects:

```json
{
  "mcpServers": {
    "context-engine-frontend": {
      "command": "/Users/yourname/.context-engine/venv/bin/python",
      "args": ["/Users/yourname/.context-engine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "/Users/yourname/projects/frontend"
      }
    },
    "context-engine-backend": {
      "command": "/Users/yourname/.context-engine/venv/bin/python",
      "args": ["/Users/yourname/.context-engine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "/Users/yourname/projects/backend"
      }
    }
  }
}
```

---

## 📦 Installation Paths

After installation, files are located at:

- **Installation:** `~/.context-engine/`
- **Virtual Environment:** `~/.context-engine/venv/`
- **MCP Server:** `~/.context-engine/mcp_server.py`
- **Config Snippet:** `~/.context-engine/mcp-config-snippet.json`
- **Activation Script:** `~/.context-engine/activate-mcp.sh`

---

## 🔧 Get Config Paths

### Get Python path:
```bash
# macOS/Linux
echo "$(cd ~/.context-engine && pwd)/venv/bin/python"

# Example output:
# /Users/yourname/.context-engine/venv/bin/python
```

### Get MCP server path:
```bash
# macOS/Linux
echo "$(cd ~/.context-engine && pwd)/mcp_server.py"

# Example output:
# /Users/yourname/.context-engine/mcp_server.py
```

### Use the config generator:
```bash
cd ~/.context-engine
python configure-mcp.py /path/to/your/project
```

This automatically:
- ✅ Detects your OS
- ✅ Finds Claude Desktop config
- ✅ Uses correct paths
- ✅ Backs up existing config
- ✅ Merges new config
- ✅ Saves a snippet

---

## 🆘 Troubleshooting

### Installation fails

**Check Python version:**
```bash
python3 --version  # Should be 3.8+
```

**Install Python 3.8+** if needed:
- macOS: `brew install python@3.11`
- Linux: `sudo apt install python3.11`

### Can't find config file

**Create directory:**
```bash
# macOS
mkdir -p ~/Library/Application\ Support/Claude

# Linux
mkdir -p ~/.config/Claude
```

**Create empty config:**
```bash
# macOS
echo '{"mcpServers": {}}' > ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
echo '{"mcpServers": {}}' > ~/.config/Claude/claude_desktop_config.json
```

### MCP not showing in Claude

1. **Completely quit Claude** (Cmd+Q on Mac)
2. **Check config** has absolute paths
3. **Restart Claude Desktop**
4. **Check logs:**
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

### Update Installation

```bash
cd ~/.context-engine
git pull
source venv/bin/activate
pip install -e .
```

---

## 🌟 What You Get

After installation, you can:

### CLI Tool:
```bash
source ~/.context-engine/activate-mcp.sh
python main.py index ./project
python main.py query "search term"
python main.py interactive
```

### MCP Server (with Claude):
- Ask Claude to search your codebase
- Get context-aware code suggestions
- Follow your existing patterns
- Understand your entire project

---

## 📖 Next Steps

1. ✅ **Installation complete?** Great!
2. 📝 **Add config to Claude Desktop**
3. 🔄 **Restart Claude Desktop**
4. 🎯 **Ask Claude about your code**
5. 📚 **Read [MCP_GUIDE.md](MCP_GUIDE.md)** for advanced features

---

## 💬 Share This!

**Easy install link:**
```
https://github.com/svsairevanth12/contextengine#easy-installation
```

**One-liner:**
```bash
curl -fsSL https://raw.githubusercontent.com/svsairevanth12/contextengine/claude/easy-mcp-install-01QbCguyLeCXRbad4kkgC7hD/install.sh | bash
```

**Config generator:**
```bash
python configure-mcp.py /path/to/project
```

---

**Questions?** Check [STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md) or [MCP_GUIDE.md](MCP_GUIDE.md)

**Your AI coding assistant is about to get way smarter!** 🧠✨
