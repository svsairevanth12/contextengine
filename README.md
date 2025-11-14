# Context Engine 🧠

> A **local, privacy-first context engine** that gives AI coding assistants superpowers through semantic code search and intelligent context retrieval.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Runs Offline](https://img.shields.io/badge/offline-100%25-green.svg)](.)

**Context Engine** stores and retrieves contextual information from your codebase using embeddings and vector search, making it easy for AI assistants like Claude, GPT, and others to understand and work with your code. Everything runs locally on your machine - no API keys, no cloud services, no data leaving your computer.

---

## 🚀 Quick Install (Recommended)

Get up and running in **under 5 minutes**:

```bash
curl -fsSL https://raw.githubusercontent.com/svsairevanth12/contextengine/claude/easy-mcp-install-01QbCguyLeCXRbad4kkgC7hD/install.sh | bash
```

This installs Context Engine as an **MCP (Model Context Protocol) server** that works with:
- ✅ **Claude Desktop** - Anthropic's official app
- ✅ **Cline** - VS Code AI assistant
- ✅ **Any MCP-compatible AI tool**

**Or install manually:** See [Installation Guide](#installation) below.

---

## ✨ What You Get

### Before Context Engine 😕
- AI assistants forget your codebase structure
- You paste code snippets manually
- Limited context = shallow understanding
- Repetitive explanations of your architecture

### After Context Engine 🎉
- **Semantic Search**: "Find all authentication handlers" works like magic
- **Smart Context**: AI sees relevant code automatically
- **Pattern Learning**: AI understands your conventions and style
- **Full Codebase Awareness**: Navigate 10k+ files effortlessly

---

## 🎯 Two Ways to Use

### 1️⃣ MCP Server (Recommended)

**Works with Claude Desktop, Cline, and other MCP clients**

After installation, Claude can:
- Search your codebase semantically
- Find similar code patterns
- Understand project structure
- Get file context automatically
- Follow your coding conventions

**Example conversation:**
```
You: Search the codebase for authentication logic
Claude: 🔍 Using context-engine MCP server...
        Found 8 relevant files with authentication code:
        - src/auth/authenticator.py (OAuth2 implementation)
        - src/middleware/auth.py (JWT middleware)
        ...
```

### 2️⃣ CLI Tool

**Direct command-line usage**

```bash
# Activate the environment
source ~/.context-engine/activate-mcp.sh

# Index your project
python main.py index ./your_project

# Search for context
python main.py query "How does the API work?"

# Interactive mode
python main.py interactive
```

---

## 🔧 Installation

### Option A: One-Line Install (MCP Server)

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/svsairevanth12/contextengine/claude/easy-mcp-install-01QbCguyLeCXRbad4kkgC7hD/install.sh | bash
```

**What it does:**
- ✅ Checks Python 3.8+
- ✅ Creates isolated environment at `~/.context-engine/`
- ✅ Installs all dependencies
- ✅ Downloads embedding model (~80MB)
- ✅ Generates MCP configuration
- ✅ Optionally auto-configures Claude Desktop

**Then:**
1. Restart Claude Desktop
2. Look for 🔌 icon in Claude
3. Ask Claude to search your codebase!

📖 **Detailed guide:** [INSTALL.md](INSTALL.md)

---

### Option B: Manual Installation (CLI + MCP)

**Prerequisites:**
- Python 3.8 or higher
- 2GB+ RAM
- ~500MB disk space for models

**Steps:**

```bash
# Clone the repository
git clone https://github.com/svsairevanth12/contextengine.git
cd contextengine

# Checkout the branch with all features
git checkout claude/local-context-engine-01QbCguyLeCXRbad4kkgC7hD

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install package
pip install -e .

# Download embedding model (one-time, ~80MB)
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Verify installation
python main.py --help
```

**Configure MCP (Optional):**
```bash
# Auto-configure Claude Desktop
python configure-mcp.py /path/to/your/project

# Or manually add to Claude Desktop config:
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Linux: ~/.config/Claude/claude_desktop_config.json
```

**MCP Configuration:**
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

📖 **Step-by-step guides:**
- [STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md) - Complete walkthrough
- [MCP_GUIDE.md](MCP_GUIDE.md) - Deep dive into MCP features
- [INSTALL.md](INSTALL.md) - Installation troubleshooting

---

## 📚 Quick Start

### Using CLI Tool

```bash
# 1. Index your codebase
python main.py index ./my_project

# Output:
# Indexing: ./my_project
# Files indexed: 47
# Chunks created: 312

# 2. Search for context
python main.py query "How does authentication work?"

# Output:
# Retrieved 8 chunks (~2847 tokens)
#
# Source: src/auth/authenticator.py
# Relevance: 0.89
# class Authenticator:
#     '''Handles user authentication...'''

# 3. Interactive mode
python main.py interactive

# >>> How do I connect to the database?
# >>> What are the API endpoints?
# >>> stats
# >>> exit
```

### Using MCP Server (with Claude Desktop)

1. **Install and configure** (see Installation above)
2. **Restart Claude Desktop** completely
3. **Verify MCP is active** - look for 🔌 icon
4. **Start asking Claude about your code:**

```
You: Search the codebase for database connection logic

Claude: I'll search your codebase for database connection code.
        [Uses MCP tool: search_codebase]

        Found 3 relevant files:

        1. src/db/connection.py (Score: 0.92)
           - DatabaseConnection class with connection pooling
           - Methods: connect(), disconnect(), execute_query()

        2. config/database.yaml (Score: 0.87)
           - Database configuration settings
        ...
```

**Available MCP Tools:**
- `search_codebase` - Semantic search across all files
- `get_file_context` - Get full context for specific files
- `find_similar_code` - Find code patterns similar to a snippet
- `get_codebase_stats` - Get overview of project structure
- `search_by_file_type` - Search within specific file types
- `find_definitions` - Find class/function definitions
- `index_paths` - Index new files or directories

**Smart Prompts:**
- `analyze_feature` - Deep dive into a feature
- `debug_error` - Find code related to an error
- `implement_similar` - Find patterns to follow
- `refactor_code` - Get context for refactoring
- `add_tests` - Find testing patterns
- `find_dependencies` - Map code dependencies

📖 **Full MCP documentation:** [MCP_GUIDE.md](MCP_GUIDE.md)

---

## 🎨 Features

### Core Capabilities

- ✅ **100% Local & Offline** - No API keys, no cloud services, all processing on your machine
- ✅ **Semantic Search** - Find code by meaning, not just keywords
- ✅ **Fast Vector Search** - ChromaDB for efficient similarity search
- ✅ **Smart Chunking** - Intelligent file parsing with overlap for better context
- ✅ **Context Assembly** - Ranks and assembles optimal context within token budgets
- ✅ **Session Management** - Persistent conversation history
- ✅ **Multi-Format Support** - Python, JavaScript, TypeScript, Java, C++, Markdown, and more
- ✅ **MCP Protocol** - Works with Claude Desktop, Cline, and other MCP clients
- ✅ **Lightweight & Fast** - Optimized for projects up to 10k files

### Technical Details

- **Embedding Model**: Sentence Transformers (all-MiniLM-L6-v2, 384-dim vectors)
- **Vector Database**: ChromaDB for local storage
- **Chunk Strategy**: 512 chars with 128-char overlap
- **Context Budget**: Configurable (default: 4000 tokens)
- **Ranking**: Hybrid similarity + keyword matching
- **Languages**: 12+ programming languages supported

---

## 🔧 Configuration

Edit `config/config.yaml` to customize:

```yaml
# Embedding Model
embedding:
  model_name: "all-MiniLM-L6-v2"  # Fast, good quality
  device: "cpu"  # Use "cuda" for GPU acceleration
  batch_size: 32

# Retrieval Settings
retriever:
  top_k: 10  # Number of results
  similarity_threshold: 0.3  # Min relevance (0-1)
  rerank: true  # Better ranking

# Context Assembly
assembler:
  max_tokens: 4000  # Max context size
  compression_enabled: true
  ranking_strategy: "hybrid"  # hybrid, similarity, or recency

# Indexer
indexer:
  chunk_size: 512  # Characters per chunk
  chunk_overlap: 128  # Overlap for continuity
  supported_extensions:
    - ".py"
    - ".js"
    - ".ts"
    - ".md"
    # Add more as needed
```

### GPU Acceleration (Optional)

For 5-10x faster embedding generation:

```bash
# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update config
# device: "cuda"
```

---

## 📖 Usage Examples

### CLI Examples

**Index a project:**
```bash
python main.py index ./myproject --recursive

# Clear and reindex
python main.py index ./myproject --clear
```

**Search for context:**
```bash
python main.py query "How do I implement OAuth?"

# Limit results
python main.py query "API endpoints" --top-k 5

# Save to file
python main.py query "database schema" --output context.txt
```

**Interactive mode:**
```bash
python main.py interactive

>>> How do I configure the database?
>>> What are the main classes?
>>> stats
>>> save session.json
>>> exit
```

**Other commands:**
```bash
# Show statistics
python main.py stats

# List sessions
python main.py sessions

# Export session
python main.py export session_id.json

# Clear database
python main.py clear
```

### MCP Examples (with Claude)

**Ask Claude:**

```
You: Search the codebase for error handling patterns
You: Find similar code to this authentication function
You: What files handle user sessions?
You: Show me the testing patterns used in this project
You: Analyze how the payment feature works
You: Find all API endpoints related to users
```

Claude will automatically use the MCP tools to search your codebase and provide accurate, context-aware responses.

### Programmatic API

```python
from context_engine import ContextEngine

# Initialize
engine = ContextEngine(config_path="config/config.yaml")

# Index files
stats = engine.index_directory("./my_project")
print(f"Indexed {stats['chunks_indexed']} chunks")

# Query for context
context = engine.query("How does the API work?", top_k=5)
print(f"Retrieved {len(context.chunks_used)} chunks")
print(context.context_text)

# Start a session
session_id = engine.start_session()

# Add conversation to memory
engine.memory.add_message("user", "How do I use the API?")
engine.memory.add_message("assistant", "Here's how...")

# Query with conversation context
context = engine.query("Tell me more", include_conversation=True)

# Metadata filtering
context = engine.query(
    "authentication logic",
    filter_metadata={"language": "python"}
)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Context Engine                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Embedder   │  │ File Indexer │  │   Memory     │    │
│  │  (Sentence   │  │  (Chunking)  │  │   Manager    │    │
│  │ Transformers)│  │              │  │  (Sessions)  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            │                                │
│                  ┌─────────▼─────────┐                     │
│                  │   Vector DB       │                     │
│                  │   (ChromaDB)      │                     │
│                  └─────────┬─────────┘                     │
│                            │                                │
│         ┌──────────────────┴──────────────────┐            │
│         │                                      │            │
│  ┌──────▼──────┐                    ┌─────────▼────────┐  │
│  │  Retriever  │                    │   Assembler      │  │
│  │ (Semantic   │───────────────────▶│  (Rank & Prune)  │  │
│  │   Search)   │                    │                  │  │
│  └─────────────┘                    └──────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              MCP Server (JSON-RPC)                   │ │
│  │  • 7 Tools  • 6 Prompts  • 4 Resources              │ │
│  └──────────────────────────────────────────────────────┘ │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  MCP Clients    │
                    │  • Claude       │
                    │  • Cline        │
                    │  • Others       │
                    └─────────────────┘
```

---

## 📁 Project Structure

```
contextengine/
├── config/
│   └── config.yaml                  # Configuration file
├── src/
│   ├── embeddings/
│   │   └── embedder.py              # Sentence transformer wrapper
│   ├── vectordb/
│   │   └── chromadb_manager.py      # Vector database interface
│   ├── indexer/
│   │   └── file_indexer.py          # File parsing and chunking
│   ├── retriever/
│   │   └── context_retriever.py     # Semantic search
│   ├── assembler/
│   │   └── context_assembler.py     # Context optimization
│   ├── memory/
│   │   └── memory_manager.py        # Session management
│   ├── mcp/
│   │   ├── server.py                # MCP protocol implementation
│   │   ├── tools.py                 # MCP tools (7 tools)
│   │   ├── prompts.py               # Smart prompts (6 prompts)
│   │   └── resources.py             # MCP resources (4 resources)
│   └── context_engine.py            # Main orchestrator
├── data/
│   ├── embeddings/                  # ChromaDB storage
│   └── sessions/                    # Session files
├── logs/                            # Log files
├── tests/
│   ├── test_engine.py               # End-to-end tests
│   └── test_mcp.py                  # MCP server tests
├── main.py                          # CLI interface
├── mcp_server.py                    # MCP server entry point
├── configure-mcp.py                 # MCP auto-configuration
├── install.sh                       # One-line installer
├── setup.py                         # Package setup
├── requirements.txt                 # Dependencies
├── README.md                        # This file
├── INSTALL.md                       # Installation guide
├── MCP_GUIDE.md                     # MCP deep dive
└── STEP_BY_STEP_GUIDE.md           # Complete walkthrough
```

---

## 🧪 Testing

Run the test suite:

```bash
# Test CLI tool
python tests/test_engine.py

# Test MCP server
python tests/test_mcp.py
```

---

## 🚨 Troubleshooting

### Installation Issues

**Python version error:**
```bash
# Check version (needs 3.8+)
python3 --version

# Install newer Python
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11
```

**Model download fails:**
```bash
# Manually download model
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### MCP Issues

**Claude doesn't show MCP tools:**
1. Completely quit Claude Desktop (Cmd+Q on Mac)
2. Check config file has absolute paths
3. Restart Claude Desktop
4. Look for 🔌 icon

**Check Claude Desktop logs:**
```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp*.log

# Linux
tail -f ~/.config/Claude/logs/mcp*.log
```

**Config file not found:**
```bash
# macOS
mkdir -p ~/Library/Application\ Support/Claude
echo '{"mcpServers": {}}' > ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
mkdir -p ~/.config/Claude
echo '{"mcpServers": {}}' > ~/.config/Claude/claude_desktop_config.json
```

### Performance Issues

**Slow indexing:**
1. Enable GPU acceleration (see Configuration)
2. Increase batch size if RAM allows
3. Use smaller/faster embedding model

**Memory issues:**
```yaml
# Reduce batch size in config.yaml
embedding:
  batch_size: 16  # Reduce from 32
```

📖 **More troubleshooting:** [INSTALL.md](INSTALL.md)

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**: Run all tests
5. **Commit**: `git commit -m "Add amazing feature"`
6. **Push**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Areas for Improvement

We'd love help with:

- **AST-based chunking** - Smarter code parsing using abstract syntax trees
- **Cross-encoder reranking** - Better result ranking
- **More file formats** - PDF, Office docs, etc.
- **Incremental indexing** - Faster updates for large codebases
- **Web interface** - Browser-based UI
- **Additional MCP tools** - More capabilities for AI assistants
- **Performance optimizations** - Speed improvements
- **Documentation** - Tutorials, videos, examples
- **Language support** - More programming languages

### Development Setup

```bash
# Clone and setup
git clone https://github.com/svsairevanth12/contextengine.git
cd contextengine
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
python tests/test_engine.py
python tests/test_mcp.py

# Code style
black src/
flake8 src/
```

### Code Standards

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Use type hints where possible
- Write clear commit messages

---

## 🐛 Reporting Issues

Found a bug? Have a feature request? Here's how to report:

### Bug Reports

**Please include:**
1. **What happened** - Describe the issue
2. **What you expected** - Expected behavior
3. **Steps to reproduce** - How to recreate the issue
4. **Environment**:
   - OS (macOS, Linux, Windows)
   - Python version
   - Context Engine version/branch
5. **Logs** - Relevant error messages
6. **Configuration** - Your config.yaml (remove sensitive info)

**Example:**
```
Title: MCP server crashes on large files

Description: When indexing files >1MB, the MCP server crashes.

Steps:
1. Index large Python file (1.2MB)
2. MCP server exits with error

Environment:
- macOS 13.2
- Python 3.11.3
- Branch: claude/local-context-engine-01QbCguyLeCXRbad4kkgC7hD

Error:
MemoryError: Unable to allocate array...
```

### Feature Requests

**Please include:**
1. **Use case** - What problem does this solve?
2. **Proposed solution** - How should it work?
3. **Alternatives** - Other approaches considered
4. **Priority** - How important is this?

### Questions & Discussions

For questions, use:
- GitHub Discussions
- Issue with `question` label

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Sentence Transformers](https://www.sbert.net/)** - Amazing embedding models
- **[ChromaDB](https://www.trychroma.com/)** - Fast vector database
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Standard for AI tool integration
- **AI Coding Assistant Community** - For inspiration and feedback

---

## 📞 Support

Need help?

- 📖 **Documentation**: Check [INSTALL.md](INSTALL.md), [MCP_GUIDE.md](MCP_GUIDE.md), [STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/svsairevanth12/contextengine/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/svsairevanth12/contextengine/discussions)
- 📝 **Verbose logging**: Run with `--verbose` flag

---

## 🎯 Use Cases

### AI Coding Assistants
Give Claude, GPT, or any AI assistant deep understanding of your codebase through semantic search and intelligent context retrieval.

### Code Navigation
Quickly find relevant code across large projects using natural language queries instead of keyword search.

### Documentation
Index and search technical documentation, making it easy to find answers to specific questions.

### Code Review
Help reviewers understand context and find related code when reviewing pull requests.

### Onboarding
Help new team members explore and understand unfamiliar codebases through conversational queries.

---

## 🌟 What Makes This Special?

- **🔒 Privacy First**: Your code never leaves your machine
- **⚡ Fast**: Optimized for real-time AI assistant interactions
- **🎯 Accurate**: Semantic search finds meaning, not just keywords
- **🔧 Flexible**: Use as CLI tool or MCP server
- **📦 Complete**: Everything needed in one package
- **🆓 Free**: Open source, MIT licensed
- **🎨 Simple**: 5-minute setup, works out of the box

---

## 📊 Performance

Tested on typical development machines:

| Metric | Value |
|--------|-------|
| Indexing speed | ~50-100 files/sec |
| Query latency | <100ms (after initial indexing) |
| Memory usage | ~500MB-1GB (depends on project size) |
| Disk space | ~2x project size (for embeddings) |
| Optimal project size | <10k files |

---

## 🚀 Roadmap

- [ ] AST-based intelligent code chunking
- [ ] Cross-encoder reranking for better accuracy
- [ ] Web UI for easier interaction
- [ ] Support for more file formats (PDF, Office)
- [ ] Incremental indexing for faster updates
- [ ] Multi-language embedding models
- [ ] Git integration (index by commit, branch)
- [ ] Workspace-aware context (multiple projects)
- [ ] Custom embedding model support
- [ ] Cloud sync option (optional)

---

**Happy Coding with Context! 🚀**

Built with ❤️ for the AI coding assistant community.

[⬆ Back to top](#context-engine-)
