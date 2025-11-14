# Step-by-Step Guide: Context Engine

This guide covers **both tools** in the Context Engine:
1. **CLI Tool** - For direct command-line usage
2. **MCP Server** - For AI coding agents (Claude Desktop, Cline, etc.)

---

# Part 1: CLI Tool - Direct Usage

## Step 1: Installation

### 1.1 Clone the Repository
```bash
# Navigate to where you want the project
cd ~/projects

# Clone the repository
git clone <your-repo-url> contextengine
cd contextengine

# Checkout the main branch (has base features)
git checkout claude/local-context-engine-01QbCguyLeCXRbad4kkgC7hD
```

### 1.2 Automated Setup (Recommended)
```bash
# Run the quick start script
./quickstart.sh
```

This will:
- ✅ Check Python version (3.8+)
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Download embedding model (~80MB)
- ✅ Create directories

**Expected Output:**
```
✓ Python version OK: Python 3.10.x
✓ Virtual environment created
✓ Dependencies installed
✓ Embedding model ready
✓ Directories created
Installation Complete!
```

### 1.3 Manual Setup (Alternative)
If quickstart.sh doesn't work:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/embeddings data/sessions logs
```

### 1.4 Verify Installation
```bash
# Activate venv if not already active
source venv/bin/activate

# Check if it works
python main.py --help
```

**Expected Output:**
```
usage: main.py [-h] [--config CONFIG] [--verbose]
               {index,query,interactive,stats,clear,sessions,export} ...

Local Context Engine for AI Coding Assistants
...
```

---

## Step 2: Index Your First Codebase

### 2.1 Index a Small Test Project

Let's index the Context Engine itself as a test:

```bash
# Make sure venv is active
source venv/bin/activate

# Index the source code
python main.py index ./src
```

**Expected Output:**
```
Initializing Context Engine...
Engine initialized successfully

Indexing: ./src
This may take a while for large codebases...

Indexing Complete!
  Files indexed: 13
  Chunks created: 156
  Total documents: 156
```

**What just happened?**
- ✅ Read all Python files in `./src`
- ✅ Split them into chunks (512 characters each)
- ✅ Generated embeddings for each chunk
- ✅ Stored in ChromaDB vector database

### 2.2 Index Your Own Project

```bash
# Index any project
python main.py index /path/to/your/project

# With options
python main.py index /path/to/your/project --recursive --clear

# Options explained:
#   --recursive : Index subdirectories (default: true)
#   --clear     : Clear existing index first
```

### 2.3 Check What Was Indexed

```bash
# Get statistics
python main.py stats
```

**Expected Output:**
```
======================================================================
Context Engine Statistics
======================================================================
Total Documents: 156
Embedding Model: all-MiniLM-L6-v2
Embedding Dimension: 384
```

---

## Step 3: Query for Context

### 3.1 Simple Query

```bash
python main.py query "How does the embedder work?"
```

**Expected Output:**
```
Query: How does the embedder work?

======================================================================
Retrieved 10 chunks (~2847 tokens)
======================================================================

============================================================
Source: src/embeddings/embedder.py
============================================================
## embedder.py (lines 15-45)
Relevance: 0.89

"""
Embedder Module - Generates vector embeddings from text using
Sentence Transformers. This module runs entirely locally without
requiring external API calls.
"""

import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

class Embedder:
    """Generates embeddings using local sentence transformer models."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", ...
...
```

### 3.2 Query with Options

```bash
# Get more results
python main.py query "database configuration" --top-k 15

# Save results to file
python main.py query "API endpoints" --output context.txt

# Combine options
python main.py query "authentication" --top-k 5 --output auth_context.txt
```

### 3.3 Disable Conversation History

```bash
# Don't include conversation context
python main.py query "error handling" --no-conversation
```

---

## Step 4: Interactive Mode (Most Useful!)

### 4.1 Start Interactive Session

```bash
python main.py interactive
```

**Expected Output:**
```
======================================================================
Context Engine - Interactive Mode
======================================================================
Started new session: a3f5e8c91b4d2e7a

Commands:
  Type your query to search for context
  'stats' - Show engine statistics
  'history' - Show conversation history
  'clear' - Clear conversation history
  'save <file>' - Export current session
  'exit' or 'quit' - Exit interactive mode

>>>
```

### 4.2 Use Interactive Mode

```bash
>>> How does the vector database work?

----------------------------------------------------------------------
Found 8 relevant chunks:
----------------------------------------------------------------------

Sources (2):
  - chromadb_manager.py
  - context_engine.py

Context Preview:
============================================================
Source: src/vectordb/chromadb_manager.py
============================================================
## chromadb_manager.py (lines 20-50)
Relevance: 0.92

"""
ChromaDB Manager - Handles vector storage and retrieval using ChromaDB.
ChromaDB is a lightweight, local vector database perfect for embedding storage.
"""
...

>>> What is the ContextEngine class?

----------------------------------------------------------------------
Found 5 relevant chunks:
----------------------------------------------------------------------
...

>>> stats

Engine Statistics:
  Total documents: 156
  Embedding model: all-MiniLM-L6-v2
  Embedding dimension: 384

Session Statistics:
  Session ID: a3f5e8c91b4d2e7a
  Total messages: 4
  Interactions: 2

>>> save my_session.json
Session exported to: my_session.json

>>> exit
Goodbye!
```

### 4.3 Load Previous Session

```bash
# Get session IDs
python main.py sessions

# Load a specific session
python main.py interactive --session a3f5e8c91b4d2e7a
```

---

## Step 5: Advanced CLI Usage

### 5.1 Clear and Reindex

```bash
# Clear entire index
python main.py clear
# Type 'yes' to confirm

# Reindex
python main.py index ./src
```

### 5.2 List All Sessions

```bash
python main.py sessions
```

**Output:**
```
Found 3 sessions:

ID: a3f5e8c91b4d2e7a
  Created: 2024-01-15T10:30:00
  Updated: 2024-01-15T11:45:00
  Interactions: 5

ID: b7f2c9d4e1a3b8c5
  Created: 2024-01-16T09:00:00
  Updated: 2024-01-16T09:30:00
  Interactions: 3
```

### 5.3 Export Sessions

```bash
# Export to JSON
python main.py export my_session.json --format json

# Export to text
python main.py export my_session.txt --format txt

# Export specific session
python main.py export output.json --session a3f5e8c91b4d2e7a
```

### 5.4 Verbose Logging

```bash
# See detailed logs
python main.py --verbose query "test"

# Logs go to logs/context_engine.log
tail -f logs/context_engine.log
```

---

## Step 6: Programmatic Usage (Python API)

### 6.1 Create a Python Script

Create `my_script.py`:

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, './src')

from context_engine import ContextEngine

# Initialize
engine = ContextEngine(config_path="config/config.yaml")

# Index your project
print("Indexing...")
stats = engine.index_directory("./my_project")
print(f"Indexed {stats['chunks_indexed']} chunks")

# Query
print("\nSearching...")
context = engine.query("How does authentication work?", top_k=5)

print(f"Found {len(context.chunks_used)} relevant chunks")
print(f"Total tokens: ~{context.total_tokens}")

# Print context
print("\nContext:")
print(context.context_text)

# Use with your LLM
prompt = f"""
Context from codebase:
{context.context_text}

Question: How does authentication work?

Answer:
"""

# Send to your LLM here
# response = your_llm.generate(prompt)
```

### 6.2 Run Your Script

```bash
source venv/bin/activate
python my_script.py
```

---

## Step 7: Configuration

### 7.1 Edit Configuration

```bash
# Open config file
nano config/config.yaml
# or
vim config/config.yaml
```

### 7.2 Key Settings to Adjust

```yaml
# Use better (but slower) model
embedding:
  model_name: "all-mpnet-base-v2"  # Higher quality
  device: "cuda"  # If you have GPU

# Adjust chunk size
indexer:
  chunk_size: 1024      # Larger chunks = more context
  chunk_overlap: 256    # More overlap = better continuity

# Get more results
retriever:
  top_k: 15             # More results
  similarity_threshold: 0.4  # Stricter matching

# Bigger context budget
assembler:
  max_tokens: 8000      # For larger context windows
```

---

# Part 2: MCP Server - For AI Agents

## Step 1: Understand What MCP Does

**MCP (Model Context Protocol)** lets AI agents (like Claude Desktop) call tools to search your codebase.

**Flow:**
1. You ask Claude: "How does authentication work?"
2. Claude calls `search_codebase("authentication")`
3. MCP server searches your indexed code
4. Returns relevant code to Claude
5. Claude answers with full context!

---

## Step 2: Install (Same as CLI)

If you already did Part 1 installation, skip this!

```bash
cd contextengine
./quickstart.sh
```

---

## Step 3: Set Up for Claude Desktop

### 3.1 Find Your Config File

**Location depends on OS:**

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### 3.2 Create Config If Doesn't Exist

```bash
# macOS
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
mkdir -p ~/.config/Claude
touch ~/.config/Claude/claude_desktop_config.json
```

### 3.3 Edit Config File

```bash
# macOS
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
nano ~/.config/Claude/claude_desktop_config.json
```

### 3.4 Add Context Engine Configuration

**IMPORTANT:** Use absolute paths!

```json
{
  "mcpServers": {
    "context-engine": {
      "command": "python",
      "args": ["/absolute/path/to/contextengine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "/absolute/path/to/your/project"
      }
    }
  }
}
```

**Example (macOS):**
```json
{
  "mcpServers": {
    "context-engine": {
      "command": "python",
      "args": ["/Users/yourname/projects/contextengine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "/Users/yourname/projects/myapp"
      }
    }
  }
}
```

**Example (Linux):**
```json
{
  "mcpServers": {
    "context-engine": {
      "command": "python",
      "args": ["/home/yourname/projects/contextengine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "/home/yourname/projects/myapp"
      }
    }
  }
}
```

### 3.5 Get Absolute Paths

```bash
# Get absolute path to mcp_server.py
cd /path/to/contextengine
pwd
# Copy this output: /Users/yourname/projects/contextengine

# Get absolute path to your project
cd /path/to/your/project
pwd
# Copy this output: /Users/yourname/projects/myapp
```

---

## Step 4: Start MCP Server

### 4.1 Test MCP Server Manually First

```bash
# Navigate to context engine
cd /path/to/contextengine

# Activate venv
source venv/bin/activate

# Test run
python mcp_server.py --codebase /path/to/your/project --log-level INFO
```

**Expected Output:**
```
INFO - Indexing codebase: /path/to/your/project
INFO - Indexed 45 files
INFO - MCP Server started successfully
```

**If it works:** Press Ctrl+C to stop. Now configure Claude Desktop!

**If it fails:** Check error messages and fix issues.

### 4.2 Common Issues

**Issue: "No module named 'sentence_transformers'"**
```bash
# Make sure venv is active
source venv/bin/activate
pip install -r requirements.txt
```

**Issue: "CODEBASE_PATH not found"**
```bash
# Check path exists
ls /path/to/your/project
# Fix the path in config
```

---

## Step 5: Configure Claude Desktop

### 5.1 Restart Claude Desktop

1. **Quit Claude Desktop completely** (Cmd+Q on Mac)
2. **Reopen Claude Desktop**
3. **Look for 🔌 icon** in the interface

### 5.2 Verify MCP is Connected

Look for the **plug icon (🔌)** or **hammer icon (🔨)** in Claude Desktop.

If you see it: **Success!** MCP is connected.

If not: Check logs

---

## Step 6: Check MCP Logs

### 6.1 View Logs

```bash
# Check Claude Desktop logs
# macOS
tail -f ~/Library/Logs/Claude/mcp*.log

# Linux
tail -f ~/.config/Claude/logs/mcp*.log
```

### 6.2 Enable Debug Logging

Edit config:
```json
{
  "mcpServers": {
    "context-engine": {
      "command": "python",
      "args": ["/path/to/mcp_server.py", "--log-level", "DEBUG"],
      "env": {
        "CODEBASE_PATH": "/path/to/project"
      }
    }
  }
}
```

---

## Step 7: Use MCP with Claude

### 7.1 Basic Usage

**Ask Claude:**
```
Search the codebase for how authentication is implemented
```

**Claude will:**
1. Call `search_codebase("authentication implementation")`
2. Get relevant code chunks
3. Analyze and explain to you

### 7.2 Example Conversations

**Example 1: Understanding Code**
```
You: How does the database connection work in this project?

Claude: Let me search the codebase...
[Calls search_codebase("database connection")]

Claude: Based on the code I found, the database connection is
handled in `src/db/connection.py`. Here's how it works:
[Explains with specific file references and line numbers]
```

**Example 2: Adding Features**
```
You: Add rate limiting to the API endpoints, similar to how
authentication works

Claude: Let me first understand the current authentication
implementation...
[Calls search_codebase("authentication middleware")]
[Calls get_file_context("src/middleware/auth.py")]

Claude: I see you're using middleware pattern for authentication.
I'll implement rate limiting following the same pattern:
[Creates rate_limit.py following your code style]
```

**Example 3: Debugging**
```
You: I'm getting "ValueError: Invalid token" during login.
Can you help?

Claude: Let me search for token validation code...
[Calls search_codebase("token validation login")]
[Calls find_definitions("validate_token")]

Claude: I found the issue. In `auth/tokens.py:45`, the token
validation expects...
[Suggests specific fix with line numbers]
```

### 7.3 Available Commands to Claude

You can ask Claude to:
- "Search the codebase for [feature]"
- "Show me the [filename] file"
- "Find code similar to [filename]"
- "Find where [ClassName] is defined"
- "Search for [topic] in Python files only"
- "Get statistics about the codebase"

---

## Step 8: Advanced MCP Usage

### 8.1 Multiple Projects

```json
{
  "mcpServers": {
    "context-engine-project-a": {
      "command": "python",
      "args": ["/path/to/contextengine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "/path/to/project-a"
      }
    },
    "context-engine-project-b": {
      "command": "python",
      "args": ["/path/to/contextengine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "/path/to/project-b"
      }
    }
  }
}
```

### 8.2 Using Smart Prompts

Ask Claude to use built-in prompts:

```
Use the analyze_feature prompt to analyze the authentication system
```

```
Use the debug_error prompt for this ValueError
```

### 8.3 Custom Configuration

Create custom config:
```bash
cp config/config.yaml config/mcp_config.yaml
nano config/mcp_config.yaml
```

Use in MCP:
```json
{
  "env": {
    "CODEBASE_PATH": "/path/to/project",
    "CONFIG_PATH": "/path/to/mcp_config.yaml"
  }
}
```

---

## Step 9: Troubleshooting

### 9.1 MCP Server Not Starting

**Check Python path:**
```bash
which python
# Use full path in config
```

**Check permissions:**
```bash
chmod +x /path/to/contextengine/mcp_server.py
```

### 9.2 No Results from Searches

**Index might be empty:**
```bash
# Check stats
python main.py stats

# Reindex if needed
python main.py index /path/to/project --clear
```

### 9.3 Claude Can't See Tools

1. **Restart Claude Desktop completely**
2. **Check config has absolute paths**
3. **Check logs for errors**
4. **Verify MCP server can start manually**

### 9.4 Slow Searches

**Reduce index size:**
```yaml
# Edit config/config.yaml
indexer:
  exclude_patterns:
    - "**/node_modules/**"
    - "**/venv/**"
    - "**/build/**"
```

**Use GPU:**
```yaml
embedding:
  device: "cuda"
```

---

## Step 10: Integration with Cline (VS Code)

### 10.1 Install Cline Extension

1. Open VS Code
2. Install "Cline" extension
3. Open Cline settings

### 10.2 Configure MCP

Add to Cline settings:
```json
{
  "mcpServers": {
    "context-engine": {
      "command": "python",
      "args": ["/absolute/path/to/contextengine/mcp_server.py"],
      "env": {
        "CODEBASE_PATH": "${workspaceFolder}"
      }
    }
  }
}
```

**Note:** `${workspaceFolder}` automatically uses your current project!

### 10.3 Use with Cline

1. Open your project in VS Code
2. Open Cline
3. Ask Cline about your code
4. Cline automatically uses MCP to search!

---

## Quick Reference

### CLI Commands
```bash
# Index
python main.py index ./project

# Query
python main.py query "search term"

# Interactive
python main.py interactive

# Stats
python main.py stats

# Clear
python main.py clear

# Sessions
python main.py sessions
python main.py export output.json
```

### MCP Server
```bash
# Test manually
python mcp_server.py --codebase /path/to/project

# With logging
python mcp_server.py --codebase /path/to/project --log-level DEBUG --log-file mcp.log
```

### Config Locations
- **Engine Config:** `config/config.yaml`
- **Claude Desktop:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
- **Cline:** VS Code settings

---

## What's Next?

1. ✅ **Try CLI first** - Get familiar with indexing and querying
2. ✅ **Set up MCP** - Configure Claude Desktop
3. ✅ **Test with small project** - Index a small codebase first
4. ✅ **Scale up** - Index your main project
5. ✅ **Read MCP_GUIDE.md** - Learn all MCP features

---

## Need Help?

- **CLI Issues:** Check `logs/context_engine.log`
- **MCP Issues:** Check Claude Desktop logs
- **General:** Read README.md and MCP_GUIDE.md
- **Verbose mode:** Add `--verbose` flag to any command

---

**You're all set! Start with the CLI, then add MCP when ready.** 🚀
