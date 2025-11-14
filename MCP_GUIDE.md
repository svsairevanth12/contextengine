# MCP Server Guide - Context Engine

## Overview

The Context Engine now includes **full MCP (Model Context Protocol) support**, allowing AI coding agents like Claude Desktop, Cline, and others to semantically search your codebase in real-time.

## 🎯 What This Enables

Your AI coding agent can now:
- 🔍 **Search your codebase semantically** - "Find authentication middleware"
- 📁 **Get context from specific files** - Understand entire file contents
- 🔗 **Find similar code** - Discover related implementations
- 📊 **Get codebase statistics** - Understand project structure
- 🎨 **Use smart prompts** - Pre-built templates for common tasks
- ⚡ **All locally** - No data leaves your machine

## 🔄 Ephemeral Indexing

**Important:** The MCP server uses ephemeral indexing for optimal performance across different codebases:

- **On Startup:** Old embeddings are cleared and the codebase is indexed fresh
- **On Shutdown:** Embeddings are deleted automatically
- **Benefits:**
  - ✅ Always fresh, up-to-date index
  - ✅ No stale data across different projects
  - ✅ Each codebase gets indexed clean
  - ✅ No disk space wasted on old embeddings

This ensures that every time you start the MCP server for a project, it gets a fresh index with the latest code changes.

## 🛠️ Available Tools

The MCP server exposes **7 powerful tools**:

### 1. `search_codebase`
Semantically search your codebase for relevant code.

**Example:**
```json
{
  "query": "How is authentication implemented?",
  "top_k": 10,
  "language": "python"
}
```

**Returns:** Relevant code chunks with file paths, line numbers, and relevance scores.

### 2. `get_file_context`
Get all indexed chunks from a specific file.

**Example:**
```json
{
  "file_path": "src/auth/authenticator.py"
}
```

**Returns:** Complete file content organized by chunks.

### 3. `find_similar_code`
Find files similar to a given file.

**Example:**
```json
{
  "file_path": "src/models/user.py",
  "top_k": 5
}
```

**Returns:** Similar files with similarity scores.

### 4. `index_paths`
Index or reindex specific files/directories.

**Example:**
```json
{
  "paths": ["./src/new_feature"],
  "clear_existing": false
}
```

**Returns:** Indexing statistics.

### 5. `get_codebase_stats`
Get statistics about the indexed codebase.

**Example:**
```json
{}
```

**Returns:** Total documents, model info, etc.

### 6. `search_by_file_type`
Search within specific file types.

**Example:**
```json
{
  "query": "API endpoints",
  "file_type": ".py",
  "top_k": 10
}
```

**Returns:** Filtered search results.

### 7. `find_definitions`
Find class, function, or variable definitions.

**Example:**
```json
{
  "name": "UserManager",
  "type": "class"
}
```

**Returns:** Definition locations with context.

## 📚 Resources

Read-only resources about your codebase:

- `codebase://stats` - Overall statistics
- `codebase://files` - List of indexed files
- `codebase://languages` - Language distribution
- `codebase://config` - Engine configuration

## 🎨 Smart Prompts

Pre-built prompt templates for common tasks:

### 1. `analyze_feature`
```json
{
  "feature": "authentication"
}
```
Analyzes how a feature is implemented with full context.

### 2. `debug_error`
```json
{
  "error_message": "ValueError: Invalid token",
  "context": "Occurs during login"
}
```
Finds code related to errors and suggests fixes.

### 3. `implement_similar`
```json
{
  "new_feature": "rate limiting",
  "similar_to": "authentication middleware"
}
```
Guides implementation based on existing patterns.

### 4. `refactor_code`
```json
{
  "target": "authentication system",
  "goal": "add type hints"
}
```
Plans refactoring with examples from codebase.

### 5. `add_tests`
```json
{
  "feature": "user authentication"
}
```
Generates tests following existing patterns.

### 6. `find_dependencies`
```json
{
  "component": "UserManager"
}
```
Analyzes dependencies and usage.

## 🚀 Setup Instructions

### Option 1: Claude Desktop (Recommended)

1. **Find your config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add Context Engine:**
   ```json
   {
     "mcpServers": {
       "context-engine": {
         "command": "python",
         "args": ["/absolute/path/to/contextengine/mcp_server.py"],
         "env": {
           "CODEBASE_PATH": "/path/to/your/project"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Verify:** Look for the 🔌 icon in Claude Desktop

### Option 2: Cline (VS Code Extension)

1. **Open Cline settings** in VS Code

2. **Add MCP server:**
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

3. **Reload VS Code**

### Option 3: Custom Integration

```python
import subprocess
import json

# Start MCP server
process = subprocess.Popen(
    ['python', '/path/to/mcp_server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    env={'CODEBASE_PATH': '/path/to/project'}
)

# Send request
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "search_codebase",
        "arguments": {
            "query": "authentication implementation",
            "top_k": 5
        }
    }
}

process.stdin.write((json.dumps(request) + '\n').encode())
process.stdin.flush()

# Read response
response = json.loads(process.stdout.readline())
print(response)
```

## 💡 Usage Examples

### Example 1: Find Authentication Code

**User asks Claude:**
> "How is user authentication implemented in this project?"

**Claude uses MCP:**
1. Calls `search_codebase("authentication implementation")`
2. Gets relevant code chunks with file paths
3. Analyzes the code and responds with detailed explanation

### Example 2: Add New Feature

**User asks:**
> "Add rate limiting to the API, similar to how authentication works"

**Claude's flow:**
1. `search_codebase("authentication middleware")` - Learn existing pattern
2. `get_file_context("src/middleware/auth.py")` - Get full auth middleware
3. `implement_similar("rate limiting", "authentication")` - Get implementation prompt
4. Creates rate limiting following the same patterns
5. `search_by_file_type("test", ".py")` - Find test patterns
6. Writes tests matching existing style

### Example 3: Debug an Error

**User asks:**
> "I'm getting 'ValueError: Invalid token' during login. Can you help?"

**Claude's flow:**
1. `debug_error("ValueError: Invalid token", "during login")` - Get debug prompt
2. Receives relevant code with context
3. Analyzes the issue
4. Suggests fix with specific file/line references

### Example 4: Refactor Code

**User asks:**
> "Refactor the authentication system to use JWT instead of sessions"

**Claude's flow:**
1. `search_codebase("authentication current implementation")`
2. `find_definitions("SessionManager", "class")`
3. `find_dependencies("SessionManager")`
4. `refactor_code("authentication", "use JWT")`
5. Gets refactoring plan with full context
6. Implements changes matching existing patterns

## 🎯 Benefits for AI Agents

### Before MCP (Agent guesses):
```
User: "Add authentication"
Agent: *Guesses where to put code*
Agent: *May not match existing patterns*
Agent: *Might miss related code*
```

### After MCP (Agent knows):
```
User: "Add authentication"
Agent: search_codebase("existing auth patterns")
Agent: get_file_context("middleware/auth.py")
Agent: *Understands existing patterns*
Agent: *Matches code style*
Agent: *Places code correctly*
Result: Consistent, high-quality implementation
```

## 📊 Performance

- **First Index:** 1-5 minutes (one-time per codebase)
- **Tool Calls:** <1 second per search
- **Memory:** ~500MB (server runs in background)
- **Updates:** Reindex changed files incrementally

## 🔒 Privacy & Security

- ✅ **100% Local** - No data sent to external services
- ✅ **No API Keys** - No external dependencies
- ✅ **Offline** - Works completely offline after model download
- ✅ **Transparent** - All code is open source

## 🐛 Troubleshooting

### Server won't start

**Check logs:**
```bash
python mcp_server.py --log-file mcp.log --log-level DEBUG
```

### Agent can't see tools

1. Verify server is running: Check for 🔌 icon
2. Check config path is absolute
3. Restart Claude Desktop/Cline
4. Check logs for errors

### Searches return no results

1. Verify codebase is indexed:
   ```bash
   # Check stats
   python main.py stats
   ```

2. Reindex if needed:
   ```bash
   python main.py index ./your_project --clear
   ```

### Slow searches

1. Index is too large - consider excluding directories:
   Edit `config/config.yaml`:
   ```yaml
   indexer:
     exclude_patterns:
       - "**/node_modules/**"
       - "**/build/**"
       - "**/dist/**"
   ```

2. Reduce chunk size for faster indexing

## 🎓 Advanced Usage

### Custom Configuration

Create custom config for MCP:

```yaml
# config/mcp_config.yaml
embedding:
  model_name: "all-mpnet-base-v2"  # Higher quality
  device: "cuda"  # Use GPU

retriever:
  top_k: 15  # More results
  similarity_threshold: 0.4  # Stricter matching
```

Use with:
```json
{
  "env": {
    "CODEBASE_PATH": "/path/to/project",
    "CONFIG_PATH": "/path/to/mcp_config.yaml"
  }
}
```

### Multiple Codebases

Run separate servers for different projects:

```json
{
  "mcpServers": {
    "context-project-a": {
      "command": "python",
      "args": ["/path/to/contextengine/mcp_server.py"],
      "env": {"CODEBASE_PATH": "/path/to/project-a"}
    },
    "context-project-b": {
      "command": "python",
      "args": ["/path/to/contextengine/mcp_server.py"],
      "env": {"CODEBASE_PATH": "/path/to/project-b"}
    }
  }
}
```

### Auto-Reindexing

Set up file watcher to reindex on changes (advanced):

```python
# watch_and_reindex.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReindexHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Call index_paths tool via MCP
        pass
```

## 📖 Protocol Details

The server implements [MCP v0.1.0](https://modelcontextprotocol.io/):

- **Transport:** stdio (JSON-RPC over stdin/stdout)
- **Methods:** tools/list, tools/call, resources/list, resources/read, prompts/list, prompts/get
- **Format:** JSON-RPC 2.0

## 🤝 Integration with Other Tools

The MCP server works with any MCP-compatible client:

- ✅ Claude Desktop
- ✅ Cline (VS Code)
- ✅ Continue.dev
- ✅ Custom integrations
- ✅ Future MCP clients

## 🚀 Next Steps

1. **Install & Configure** - Set up MCP server for your agent
2. **Index Your Codebase** - Let it index your project
3. **Try It Out** - Ask your agent coding questions
4. **Explore Tools** - Use different tools for different tasks
5. **Use Prompts** - Try the smart prompts for complex tasks

---

**Your AI coding agent just got a whole lot smarter! 🧠✨**

For questions or issues, check the main README.md or open an issue on GitHub.
